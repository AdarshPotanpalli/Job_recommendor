# Job Recommendation Website

A Flask-based job recommendation system that allows users to upload resumes in PDF format and receive personalized job recommendations based on their skills and preferences. The system leverages machine learning techniques and collaborative filtering to suggest the most relevant job listings.

## Features

- **User Authentication:** Users can sign up, log in, and log out securely.
- **Resume Upload:** Users can upload their resumes in PDF format.
- **Resume Parsing:** The system extracts and cleans text from the uploaded resume.
- **Job Title Prediction:** A Random Forest classifier predicts the most relevant job title for the user based on their resume.
- **Job Listing Scraping:** Job listings are scraped from online sources using the predicted job title as a filter.
- **Personalized Job Recommendations:** Uses collaborative filtering with Cosine Similarity to match job listings with the user's skills.
- **"More Like This" Recommendations:** Users can get additional recommendations based on jobs they liked.
- **Archives Page** The jobs selected by the user is archived in the Archives page

## Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** Jinja2 (HTML, CSS, JavaScript)
- **Database:** SQLite3
- **Machine Learning:**
  - Text extraction and cleaning
  - TF-IDF vectorization
  - Random Forest classifier (for job title prediction)
  - Cosine Similarity (for job recommendations)
- **Scraping:** Beautiful Soup (following the robots.txt norms)

## Project Structure

```
📁 Job_recommendor/
│-- run.py  # Main entry point to launch the Flask app
│-- instance/  # Stores SQLite3 database files
│-- recommendor/  # Custom python package handling job recommendations
│   │-- templates/  # Jinja2 and html templates for frontend pages
│   │-- static/  # CSS, Images, and assets for frontend
│   │-- forms.py # Flask Forms and validations
│   │-- routes.py # Flask App routes
│   │-- models.py # SQLAlchemy Models
│   │-- ml_stack.py # ML and NLP Stack for getting job recommendations  
│-- models/
│   ├── model.ipynb  # EDA and training of job title classifier using Kaggle's resume dataset 
│-- requirements.txt  # Dependencies and libraries
│-- README.md  # Documentation
```

## Installation & Setup

1. **Clone the Repository**
   ```sh
   git clone https://github.com/AdarshPotanpalli/Job_recommendor.git
   cd Job_redommendor
   ```
2. **Create and Activate Virtual Environment**
   ```sh
   
   conda create --name myenv python=3.9
   conda activate myenv
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the Application**
   ```sh
   python run.py
   ```
5. **Access the Website**
   Open a browser and go to `http://127.0.0.1:5000/`

## License

This project is open-source and available under the MIT License.

---
>**Author:** Adarsh Potanpalli 
>
>**Email:** p.adarsh.24072001@gmail.com 

