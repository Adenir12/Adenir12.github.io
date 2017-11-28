from google.appengine.ext import db

#for students
class Student(db.Model):
	first_name = db.StringProperty(required=False)
	last_name = db.StringProperty(required=False)
	email = db.StringProperty(required=False)
	phone = db.StringProperty(required=False)
	password = db.StringProperty(required=False)
	college = db.StringProperty(required=False)
	address = db.StringProperty(required=False)
	gender = db.StringProperty(required=False)
	bday = db.StringProperty(required=False)

#information about companies that can post internships
class Company(db.Model):
	cp_name = db.StringProperty(required=False)
	cp_email = db.StringProperty(required=False)
	cp_phone = db.StringProperty(required=False)
	cp_password = db.StringProperty(required=False)
	cp_website = db.StringProperty(required=False)
	cp_address = db.StringProperty(required=False)

#stores information about the internships posted by the companies
class Internship(db.Model):
    companyname = db.StringProperty(required=True)
    location = db.StringProperty(required=True)
    website = db.StringProperty(required=True)
    c_email = db.StringProperty(required=True)
    intern_posi = db.StringProperty(required=True)
    c_phone = db.StringProperty(required=True)
    deadline = db.StringProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
    postedby = db.StringProperty(required=True)

class Reviews(db.Model):
	"""docstring for Reviewa"""
	review = db.TextProperty(required=True)
	review_posted_by = db.StringProperty(required=True)
	created = db.DateProperty(auto_now_add=True)
		
