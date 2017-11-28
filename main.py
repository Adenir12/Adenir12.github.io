import webapp2
import jinja2
import os
import hashlib
import hmac
import database
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import mail

#concatenates this secret string to cookies to make it more secure
secret = "jksdhkjsdhn+787897897987896798" 

#joins the path of current direcotry with template
temp_dir = os.path.join(os.path.dirname(__file__),'templates')

#loads the file in jinja environment from temp_dir path
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(temp_dir),autoescape=True)

def render_str(template,**params):
    t = jinja_env.get_template(template)
    return t.render(params)

#hashes the password. comes handy if someone tries to compromise the database
#there is even secure hashing function using salt, but this will be ok for now
def hash_str(s):            
    return hashlib.sha224(s).hexdigest()

def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

#All the classes below inherits from Handler class
class Handler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(Handler, self).__init__(request=None, response=None)
        self.request = request
        self.response = response
        uid = self.read_secure_cookie('user_id')
        self.loged_user =  uid and database.Student.get_by_id(int(uid))

        #for company
        self.loged_cp_user =  uid and database.Company.get_by_id(int(uid))
    # render the general string like hello world
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    # render the string with <html></html> tags
    def render_str(self, template, **params):
        params['user'] = self.loged_user
        t = jinja_env.get_template(template)
        return t.render(params)
        # read the file and pass strig to the previous function
    
    #renderer for company after login
    def render_cp_str(self, template, **params):
        params['user'] = self.loged_cp_user
        t = jinja_env.get_template(template)
        return t.cp_render(params)

    def cp_render(self,template,**kw):
        self.write(self.render_cp_str(template,**kw))

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))
    # set the cookies when the user logs in
    def set_secure_cookie(self, name, val):
        cookie_val = str(make_secure_val(val))
        self.response.headers.add_header('Set-Cookie','%s=%s; Path=/'%(name, cookie_val))

    # reads the hashes cookie form the browser
    def read_secure_cookie(self,name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)
    # logs the user on and sets cookies
    def login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))

    def cp_login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))

    #clears all the cookies if the user logs out
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

class MainHandler(Handler):
    def get(self):
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        self.render("main.html", logged_user=usr, logged_cp_usr = cp_usr)
        
class ContactHandler(Handler):
    def get(self):  #renders the signup html
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        self.render("contactus.html", logged_user=usr, logged_cp_usr = cp_usr)
    #gets the data from signup and updates the imported database

class ContactusHandler(Handler):
    def get(self):  #renders the login html
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        self.render("aboutus.html", logged_user = usr, logged_cp_usr = cp_usr)

#shows the list of internships in internships.html
class InternshipHandler(Handler):
    def get(self):
        internships = db.GqlQuery("SELECT * FROM Internship "
                                "ORDER BY created DESC ")
        print type(internships)
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        self.render("internships.html", logged_user=usr, internships=internships, logged_cp_usr = cp_usr)

class signupHandler(Handler):
    def get(self):  #renders the signup html for students
        self.render("signup.html")

    def post(self):
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        email = self.request.get('email')
        password = self.request.get('password')
        phone = self.request.get('phone')
        address = self.request.get('address')
        college = self.request.get('college')
        gender = self.request.get('gender')
        bday = self.request.get('bday')
        # pp = self.request.get('userphoto')
        usr = database.Student.all().filter('email =', email).get()
        if usr:
            error = "You have already signed up. Please go to login page."
            self.render("signup.html", error=error)
        else:    
            mail.send_mail(sender='bikki.nagarkoti@gmail.com',
                       to=email,
                       subject="Welcome to Nepal Internships",
                       body="""Dear """ + firstname + """,""" +"""
                Welcome to Nepal Internships. We hope you will find it very useful applying to internships.

    The Nepal Internships Team.
    http://nepainternships.appspot.com/""")

            database.Student(first_name=firstname, last_name=lastname, email = email, phone = phone, password = hash_str(password.strip()), college = college, address = address,
                          gender = gender, bday = bday).put()
            self.redirect('/')

class companySignupHandler(Handler):
    def get(self):  #renders the company registration html
        self.render("cp-register.html")

    def post(self):
        cp_name = self.request.get('cp_name')
        cp_email = self.request.get('cp_email')
        cp_phone = self.request.get('cp_phone')
        cp_password = self.request.get('cp_password')
        cp_website = self.request.get('cp_website')
        cp_address = self.request.get('cp_address')
        #stores information about company in Company entity
        cp_usr = database.Company.all().filter('cp_email =', cp_email).get()
        if cp_usr:
            error = "You have already signed up. Please go to login page."
            self.render("cp-register.html", error = error, cp_email=cp_email);
        else:
            database.Company(cp_name=cp_name, cp_email=cp_email, cp_phone = cp_phone, cp_password = hash_str(cp_password.strip()), cp_website = cp_website, cp_address = cp_address).put()
            self.redirect('/')

class postinternshipHandler(Handler):
    def get(self):
        cp_usr = self.loged_cp_user
        self.render("postinternship.html", logged_cp_usr = cp_usr)

    def post(self):
        companyname = self.request.get('companyname')
        location = self.request.get('location')
        website = self.request.get('website')
        c_email = self.request.get('c_email')
        intern_posi = self.request.get('intern_posi')
        c_phone = self.request.get('c_phone')
        deadline = self.request.get('deadline')
        postedby = self.loged_cp_user.cp_name
        # pp = self.request.get('userphoto')

        internshipsdb = database.Internship(companyname=companyname, location=location, website = website, c_email = c_email, intern_posi = intern_posi,
                      c_phone = c_phone, deadline = deadline, postedby=postedby)
        internshipsdb.put()
        self.redirect('/')

class loginHandler(Handler):
    def get(self):  #if the user is logged in, redirects to home
        if self.loged_user:
            self.redirect('/')
        elif self.loged_cp_user:
            self.redirect('/')
        else:
            self.render("login.html")

    def post(self):
        email = self.request.get('email')
        password = hash_str(self.request.get('password'))
        if(password and email):
            usr = database.Student.all().filter('email =', email).get()
            cp_usr = database.Company.all().filter('cp_email =', email).get()
            if usr:
                if  password != usr.password:
                    error = "Password did not match. Try again. "
                    self.render("login.html", error = error, email=email);
                else:
                    self.login(usr)
                    self.redirect('/')
            #checks also for company email and password information
            elif cp_usr:
                if password != cp_usr.cp_password:
                    error = "Password did not match. Try again. "
                    self.render("login.html", error = error, email=email);
                else:
                    self.cp_login(cp_usr)
                    self.redirect('/')
            else:
                error = 'Email not found. Please signup first.'
                self.render("login.html", error = error, email=email)
        else:
            error = 'Both fields are required.'
            self.render("login.html", error = error)

class LogoutHandler(Handler):
    def post(self):
        self.logout()
        self.redirect('/')

#shows information about the loggedin student information
class MyProfileHandler(Handler):
    def get(self):
        usr = self.loged_user
        self.render("myprofile.html", logged_user=usr)
#shows information about the loggedin company information
class CompanyProfileHandler(Handler):
    def get(self):
        cp_usr = self.loged_cp_user
        self.render("companyprofile.html", logged_cp_usr = cp_usr)

class ThisCompanyProfileHandler(Handler):
    def get(self, company):
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        this_cp_name = database.Company.all().filter('cp_name =', company).get()
        self.render("thiscompany.html", this_cp_name = this_cp_name, logged_user=usr, logged_cp_usr = cp_usr)

class ReviewerHandler(Handler):
    """docstring for Re"""
    def get(self, reviewer):
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        if (reviewer == "Anonymous"):
            self.render("postedbyninja.html")
        else:
            reviewer_name = reviewer.split()[0]
            this_usr_name = database.Student.all().filter('first_name =', reviewer_name).get()
            this_cp_name = database.Company.all().filter('cp_name =', reviewer).get()
            if this_usr_name:
                self.render("thisuser.html", this_usr_name=this_usr_name, logged_user=usr, logged_cp_usr = cp_usr)
            else:
                self.render("thiscompany.html", this_cp_name = this_cp_name, logged_user=usr, logged_cp_usr = cp_usr)

class ReviewsHandler(Handler):
    def get(self):
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        reviews = db.GqlQuery("SELECT * FROM Reviews "
                                "ORDER BY created DESC ")
        self.render("reviews.html", logged_user=usr, logged_cp_usr = cp_usr, reviews=reviews)


    def post(self):
        usr = self.loged_user
        cp_usr = self.loged_cp_user
        review = self.request.get('review')
        if (review == ""):
            reviews = db.GqlQuery("SELECT * FROM Reviews "
                                "ORDER BY created DESC ")
            error = "Oops you cannot post an empty review. Please write something. :)"
            self.render("reviews.html", logged_user=usr, logged_cp_usr = cp_usr, error=error, reviews=reviews)
            
        else:
            if usr:
                review_posted_by = usr.first_name + " " +usr.last_name
            elif cp_usr:
                review_posted_by = cp_usr.cp_name
            else:
                review_posted_by = "Anonymous"
            reviewsdb = database.Reviews(review=review, review_posted_by=review_posted_by)
            reviewsdb.put()
            self.redirect('/reviews')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/aboutus', ContactusHandler),
    ('/internships', InternshipHandler),
    ('/signup', signupHandler),
    ('/cp-register', companySignupHandler),
    ('/login', loginHandler),
    ('/login', loginHandler),
    ('/logout', LogoutHandler),
    ('/myprofile', MyProfileHandler),
    ('/reviews', ReviewsHandler),
    ('/companyprofile', CompanyProfileHandler),
    ('/thiscompany/(.*)', ThisCompanyProfileHandler),
    ('/reviewer/(.*)', ReviewerHandler),
    ('/postinternship', postinternshipHandler),

], debug=True)