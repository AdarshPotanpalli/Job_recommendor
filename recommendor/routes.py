from recommendor import app, db
from flask import render_template, redirect, url_for, flash, request
from recommendor.forms import RegisterForm, LoginForm, ResumeUploadForm, ArchiveForm
from recommendor.models import User, Jobs, user_jobs
from flask_login import login_user, logout_user, login_required, current_user
from recommendor.ml_stack import get_job_recommendation, extract_text_from_pdf
from werkzeug.utils import secure_filename
import os
import glob
import ast
from flask import session

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home Page route
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

# Recommendor Page Route
@app.route('/recommendor', methods = ['GET', 'POST'])
@login_required
def recommendor_page():
    resume_upload_form = ResumeUploadForm()
    archive_form = ArchiveForm()
    
    if request.method == 'POST':
        if request.files.get('resume'): # on clicking Upload and get recommendations   
            if 'resume' not in request.files:
                flash("No file uploaded!", category="danger")
                return redirect(url_for('recommendor_page'))
            
            file = request.files['resume']
            
            if file.filename == '':
                flash("Please select a PDF file.", category="warning")
                return redirect(url_for('recommendor_page'))
            
            if not file.filename.endswith('.pdf'):
                flash("Only PDF files are allowed.", category="danger")
                return redirect(url_for('recommendor_page'))
            
            if file:
                session.pop('Latest_job_skills', None)
                session.pop('Latest_job_title', None)
                session.pop('Latest_job_exp', None)
                session.pop('Latest_job_id', None)

                paths = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*pdf'))
                if len(paths)>0:
                    file_path = paths[0]
                    os.remove(file_path)# remove the already present resume pdfs from the uploads
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
            else:
                flash("Invalid file", category='danger')
        
        if request.form.get('more_like_this'): # on clicking More Like This
            job = request.form.get('more_like_this')
            job = ast.literal_eval(job) # converting to dict
            session['Latest_job_title'] = job['JobTitle']
            session['Latest_job_exp'] = job['ExperienceRequired']
            session['Latest_job_id'] = job['JobID']
            session['Latest_job_skills'] = job['SkillsRequired']

            job_item = Jobs.query.filter_by(id = job['JobID']).first()
            if job_item: # if the job item already exists in the Jobs table
                existing_job = next((job for job in current_user.jobs if job.id == job_item.id), None)
                if existing_job: # if the current user already has this job in the archives
                    print("Current user already has this job in the list!")
                else:
                    current_user.jobs.append(job_item)
                    db.session.commit()
            else: # create the job Item
                job_item = Jobs(id = job['JobID'],
                                company_name = job['CompanyName'],
                                job_title = job['JobTitle'],
                                skills_required = job['SkillsRequired'],
                                posting_time = job['PostingTime'],
                                experience_required = job['ExperienceRequired'],
                                more_information = job['MoreInformation'],)
                db.session.add(job_item)
                current_user.jobs.append(job_item)
                db.session.commit()
            
        return redirect(url_for('recommendor_page'))

    if request.method == 'GET':
        
        Latest_job_title = session.get('Latest_job_title', "")
        Latest_job_exp = session.get('Latest_job_exp', 0)
        Latest_job_id = session.get('Latest_job_id', "")
        Latest_job_skills = session.get('Latest_job_skills', "")    
        
        # Process the PDF file and generate job recommendations
        paths = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*pdf'))
        if len(paths)>0:
            file_path = paths[0]
            resume_text = extract_text_from_pdf(file_path)
            if Latest_job_title != "":
                jobs_df = get_job_recommendation(resume_text= resume_text, 
                                                 job_category= Latest_job_title, 
                                                 exp = int(Latest_job_exp[0]),
                                                 skills_selected= Latest_job_skills,
                                                 job_id_selected= Latest_job_id)
            else:
                jobs_df = get_job_recommendation(resume_text)  # Function to extract skills and match jobs
            
            jobs_list_of_dict = jobs_df.to_dict(orient='records')
        else:
            jobs_list_of_dict = []
        
        return render_template('recommendor.html', jobs = jobs_list_of_dict, resume_upload_form = resume_upload_form, archive_form = archive_form)

# Archives Page route
@app.route('/archives')
def archives_page():
    jobs_under_current_user = current_user.jobs
    return render_template('archives.html', jobs = jobs_under_current_user)

# Register Page route
@app.route('/register', methods = ['GET', 'POST'])
def register_page():
    
    register_form = RegisterForm()
    # validation and user creation on clicking 'Create Account' in Register Page
    if register_form.validate_on_submit(): 
        user_to_create = User(user_name = register_form.username.data,
                              email_address = register_form.email.data,
                              password = register_form.password1.data)
        
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create) #login the user on account creation
        flash(f"Account created successfully, welcome {user_to_create.user_name}!", category= 'success') # flashing the success message
        return redirect(url_for('recommendor_page')) # redirect to recommendor page
        
    # flashing the error messages  
    if register_form.errors != {}:
        for error in register_form.errors.values():
            flash(f"Error in Account Creation: {error[0]}", category = 'danger')
    
    return render_template('register.html', form = register_form)

# Login Page route
@app.route('/login', methods = ['GET', 'POST'])
def login_page():
    
    login_form = LoginForm()
    # validation and login on clicking 'Login' in Login Page
    if login_form.validate_on_submit():
        user_to_login = User.query.filter_by(user_name = login_form.username.data).first() # check if there is any user with the given username
        if user_to_login and user_to_login.check_form_correction(
            password_to_check =login_form.password.data
        ): 
            login_user(user_to_login) #login the user
            flash(f"Welcome {user_to_login.user_name}!", category='info')
            return redirect(url_for('recommendor_page'))
        else:
            flash("Either Username or Password is incorrect, please check your credentials!", category='danger')
        
    return render_template('login.html', form = login_form)

# Logout Page route
@app.route('/logout')
def logout_page():
    logout_user()
    flash("Logged out successfully!", category='success')
    return redirect(url_for('home_page'))