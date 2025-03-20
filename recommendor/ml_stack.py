from bs4 import BeautifulSoup
import requests
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
import string
import nltk
from nltk.corpus import stopwords
import re
import os
english_stopwords = stopwords.words('english')
import time
import PyPDF2
import pickle

def extract_text_from_pdf(pdf_path):
    
    """function to extract text from resume pdf file
    Args:
        pdf_path: path of the pdf file
    """
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        
        # Loop through all the pages and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    
    return text


def text_cleaning(resume_text: str):

    """function to clean the dataset

    Args:
        resume_text: a string of resume text

    Returns:
        A cleaned list of words in resume
    
    """
    # lower case
    resume_text = resume_text.lower()
    # remove urls, http, https, www
    resume_text = re.sub(r'https?://\S+|www\.\S+', ' ', resume_text)
    # removing the puncuation
    resume_text = ''.join([s for s in resume_text if s not in string.punctuation])
    # removing \r and \n in resume text
    resume_text = re.sub(r'[\r\n]+', ' ', resume_text)
    # removing words containing digits
    resume_text = re.sub(r'\w*\d\w*', ' ', resume_text)
    # removing words containing special characters
    resume_text = re.sub(r'\W', ' ', resume_text)
    # removing encoding artifacts
    resume_text = re.sub(r'[âÃ€™|â€™|Ã¢|Ã¦]+', ' ', resume_text)
    # removing non-ASCII characters
    resume_text = re.sub(r'[^\x00-\x7F]+', ' ', resume_text)
    # lower case
    resume_text.lower()
    # remove stopwords
    resume_text = [word for word in resume_text.split() if word not in english_stopwords]

    # return a list of words
    return resume_text

def get_job_recommendation(resume_text, k = 5, job_category = None, exp = None, skills_selected = None, job_id_selected = None):

    """ Top k recommendations based on the resume text

    If the user has no jobs saved in his/her archive, then the resume text and
    the category predictor based on resume text is used for recommendation.
    
    If the user has atleast 1 job archived, then the resume text and the user's
    job archive is used for recommendation.

    Args:
        resume_text: a string of resume text
        k: number of recommendations
        job_category: job category as String (extracted from User's selection)
        exp: experience in year (extracted from user's selection)
        skills_selected: skills as string (extracted from user's selection)
        job_id_selected: job id (extracted from user's selection)

    Returns:
        Top k job recommendations as a pandas DataFrame
    
    """
    
    # if there are no job lists saved in user's archive, use the category predictor for job filtering
    html_text = ""
    while "<h1>Oops!</h1>" in html_text or len(html_text) == 0:
        
        if exp:
            # use latest element in user's archive for job filtering
            # just to give an example
            keyword = '+'.join(job_category.split())
            html_text = requests.get(f"https://m.timesjobs.com/mobile/jobs-search-result.html?txtKeywords={keyword}&cboWorkExp1={exp}&txtLocation=").text
        else:
            #job category prediction
            
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the full path to 'pipeline.pkl'
            file_path = os.path.join(script_dir, 'pipeline.pkl')
            # Loading pipeline
            with open(file_path, 'rb') as f:
                pipeline_loaded = pickle.load(f)
            # get the prediction
            job_category = pipeline_loaded.predict([resume_text])[0]
            
            print(f"According to your resume, we would give you a first set of job recommendation for role: {pipeline_loaded.predict([resume_text])[0]}")
            keyword = '+'.join(job_category.split())
            html_text = requests.get(f"https://m.timesjobs.com/mobile/jobs-search-result.html?txtKeywords={keyword}&cboWorkExp1=1&txtLocation=").text

        if "<h1>Oops!</h1>" in html_text:
            print("Some problem occured, trying again..")
            time.sleep(5) # sleep for 5 seconds

    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('div', class_ = 'srp-listing clearfix') # finding all job containers

    jobs_web = {
        'CompanyName': [],
        'JobID' : [],
        'JobTitle': [],
        'SkillsRequired': [], 
        'PostingTime': [], 
        'ExperienceRequired': [], 
        'MoreInformation': []
    }
    for job in jobs:
        job_heading = job.find('div', class_ = 'srp-job-heading')
        more_info = job_heading.h3.a['href'] # more information
        job_id = job.get('id') #job id
        job_title = job_heading.h3.a.text # job title
        comp_name = job.find('span', class_ = 'srp-comp-name').text #company name
        posting_time = job.find('span', class_ = 'posting-time').text #posting time
        skills = job.find_all('a', class_ = 'srphglt') #skills
        skills_text = ' | '.join(skill.text for skill in skills)
        experience_required = job.find('div', class_ = 'srp-exp').text # experience required

        if job_id != job_id_selected:
            # appending the list of dictionaries
            jobs_web['CompanyName'].append(comp_name)
            jobs_web['JobID'].append(job_id)
            jobs_web['JobTitle'].append(job_title)
            jobs_web['SkillsRequired'].append(skills_text)
            jobs_web['PostingTime'].append(posting_time)
            jobs_web['ExperienceRequired'].append(experience_required)
            jobs_web['MoreInformation'].append(more_info)

    # creating a dataframe of jobs
    jobs_web_df = pd.DataFrame(data=jobs_web)

    # Count vectorizer
    vectorizer = CountVectorizer(analyzer= text_cleaning)
    count_transformer = vectorizer.fit(jobs_web_df['SkillsRequired'])

    # Filter the resume text based on the text in skills section of jobs_web_df
    skills_list = jobs_web_df['SkillsRequired'].apply(lambda x: x.split())
    
    # getting a skill filter for resume
    unique_skills = set()
    for skills in skills_list:
        for skill in skills:
            unique_skills.add(skill)
    unique_skills_filter = text_cleaning(' '.join(list(unique_skills)))
    
    # filtering the resume text
    if skills_selected:
        resume_text = text_cleaning(skills_selected)
    else:
        resume_text = text_cleaning(resume_text)
    resume_text = [word for word in resume_text if word in unique_skills_filter]
    resume_text = list(set(resume_text))

    #obtain cosine similarity score between resume text and skills text
    similarity_score = cosine_similarity(count_transformer.transform([' '.join(resume_text)]), count_transformer.transform(jobs_web_df['SkillsRequired']))
    
    # sort(in descending order) the df based on the similarity score, and get the first k elements as recommendation
    return jobs_web_df.iloc[similarity_score.argsort()[0][::-1][:k]]