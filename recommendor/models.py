from recommendor import db, bcrypt, login_manager
from flask_login import UserMixin

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Association table for Many to Many relationship
user_jobs = db.Table('user_jobs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('job_id', db.String, db.ForeignKey('jobs.id'), primary_key=True)
)

# User table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), nullable = False, primary_key = True)
    user_name = db.Column(db.String(length = 30), nullable= False, unique = True)
    email_address  = db.Column(db.String(length = 50), nullable = False, unique = True)
    password_hash = db.Column(db.String(length = 60), nullable = False)
    jobs = db.relationship('Jobs', secondary=user_jobs, backref=db.backref('owners', lazy='dynamic')) # a list of elements of type Jobs
    
    #Getter
    @property
    def password(self):
        return self.password_hash # returns password hash
    
    #Setter
    @password.setter
    def password(self, password_plain_text):
        self.password_hash = bcrypt.generate_password_hash(password_plain_text).decode('utf-8') # sets the hashed password
        
    def check_form_correction(self, password_to_check):
        return bcrypt.check_password_hash(self.password_hash, password_to_check) # returns if the password is correct or not
    
    
# Jobs table 
class Jobs(db.Model):  
    id = db.Column(db.String(), nullable = False, primary_key = True) # unique id of each job
    company_name = db.Column(db.String(length = 100), nullable = False)
    job_title = db.Column(db.String(length = 100), nullable = False)
    skills_required = db.Column(db.String())
    posting_time = db.Column(db.String(length = 20))
    experience_required = db.Column(db.String(), nullable = False)
    more_information = db.Column(db.String())
    
    def __repr__(self):
        return f"Job: {self.job_title}"