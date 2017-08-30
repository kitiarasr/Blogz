

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "blablabla"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    #this says for every owner, populate list task with their corresponding tasks

    def __init__(self, username, password):
        self.username = username
        self.password = password
       

@app.before_request   #i guess prevents app.route login from kicking in gear and putting multiple emails in a session
def require_login():    #as a result.. so maybe if email is in session, skip login?
    allowed_routes = ['login', 'register', 'blog', 'view', 'home', 'viewUserBlogs'] #"white list"
    #request is the object flask makes to represent http request, and endpoint is the given path
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
        #first condition: if direct is not in allowed routes or user is not logged in,
        #redirect to user log in

@app.route('/home', methods =['POST', 'GET'])
def home():  #allowed routes are the NAMES of the functions
    all_users = User.query.filter_by().all()
    return render_template('home.html', all_users=all_users)


@app.route('/viewUserBlogs', methods =['GET'])
def viewUserBlogs():  #allowed routes are the NAMES of the functions
    id = request.args.get('id')
    blogs = Blog.query.filter_by(owner_id=id).all()
    return render_template('viewUserBlogs.html', all_blogs=blogs)



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': # means someone is trying to login
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password: # if user was found and password too
            session['username'] = username  #allows us to "remember" a user LOGGED in.
            #session is a dictionary, where data is saved and i guess
            #information that is put into dictionary can only be done so once
            flash("Logged in") #flash passes this variable to template
            print(session)
            #flash actually saves value corresponding to session inside,
            #bec in this case theres no way to pass in value here because there
            #is no render template used
            #return redirect('/newpost') !!!!!!!!!!!!!!!!!!!!!!!
            return redirect('/newpost')
        else:
            # TODO - explain why login failed
            flash('User password incorrect, or user does not exist', 'error') #message, category, reverse in template
    return render_template('login.html')


@app.route('/newpost', methods=['POST', 'GET']) #when i first get into page, its a get request, so if statement is needed in order 
def newpost():
    if request.method == 'POST':
        #check if user is logged in at all
        title = request.form['title']
        body = request.form['body'] 
        owner = User.query.filter_by(username=session['username']).first()
        if title != "" and body != "":
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
          #  session['title'] = title
            
            return render_template ('view.html', title=title, body=body)
        else:
            flash("Please try again")
            render_template("newpost.html")
       
    return render_template("newpost.html")


@app.route('/blog', methods=['POST', 'GET']) #when i first get into page, its a get request, so if statement is needed in order 
def blog():
    
    blogs = Blog.query.filter_by().all()

    return render_template('blog.html', blogs=blogs)



@app.route('/view', methods=['GET']) #when i first get into page, its a get request, so if statement is needed in order 
def view():
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    return render_template("view.html", title=blog.title, body=blog.body)



@app.route('/logout')
def logout():
    del session['username'] #remove users username from the session
    print(session)
    return redirect('/blog')


@app.route('/register', methods =['POST', 'GET'])
def register():
    if request.method == 'POST':
        #TODO - validate users data 
        username = request.form['username']
        password = request.form['password']
        verifyPassword = request.form['verify']
        existing_user = User.query.filter_by(username=username).first() 

        if password != verifyPassword:
            flash('passwords do not match')
           # redirect('/register')
        elif len(username) < 3 or len(password) < 3 or len(verifyPassword) < 3:
            flash('username or password cannot be less than 3 characters.')
        elif not existing_user:           # if user doesnt exist, put in database
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
        # TODO - "remember" the user, that user has logged in from one request to another
            return redirect ('/newpost')       # redirect back to home
        else:           #if user exists, display string saying you already have user in db
             #TODO - user better response messaging
            flash("User already exists")

    return render_template('register.html')




if __name__ == '__main__':
    app.run()
