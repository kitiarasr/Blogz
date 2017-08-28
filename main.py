

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "blablabla"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)


    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET']) #when i first get into page, its a get request, so if statement is needed in order 
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body'] 
        if title != "" or body != "":
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            session['title'] = title
            
            return render_template ('view.html', title=title, body=body)
        else:
            flash("Please try again")
            redirect('/newpost')
       
    return render_template("newpost.html")


@app.route('/blog', methods=['POST', 'GET']) #when i first get into page, its a get request, so if statement is needed in order 
def blog():
    posts = Blog.query.filter_by().all()
    return render_template("blog.html", posts=posts)



@app.route('/view', methods=['GET']) #when i first get into page, its a get request, so if statement is needed in order 
def view():
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    return render_template("view.html", title=blog.title, body=blog.body)

if __name__ == '__main__':
    app.run()
