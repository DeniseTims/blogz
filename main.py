from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import cgi
import flask

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:test@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text(560))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request
def require_login():
    allow_routes = ['login', 'signup', 'index', 'blog', 'single_User', 'logout']
    if request.endpoint not in allow_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verified = request.form['verify']
        if username == '':
            username_not_found = "enter user name"
            return render_template('signup.html', user_error=username_not_found)
        if password == '':
            password_not_found = "enter password"
            return render_template('signup.html', pw_error=password_not_found)
        if verified == '':
            not_verified = "verify password"
            return render_template('signup.html', vfy_error=not_verified)
        if password != verified:
            passwords_not_matching = "passwords do not match"
            return render_template('signup.html', match_error=passwords_not_matching)
        if len(username) < 3:
            invalid_user = 'username needs to be at least 3 characters'
            return render_template('signup.html', inval_user_err=invalid_user)
        if len(password) < 3:
            invalid_password = 'password needs to be at least 3 characters'
            return render_template('signup.html', inval_pass_err=invalid_password)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        if existing_user:
            username_exists = 'this user name already exists!'
            return render_template('signup.html', error=username_exists)

    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            user_not_found = 'user unknown'
            return render_template('login.html', error=user_not_found)

    if request.method == 'GET':
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
        return redirect('/blog')
    else:
        return redirect('/blog')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    posts = Blog.query.all()
    return render_template('index.html', users=users, posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
        if request.method == 'GET':
            return render_template('new_posts.html')

@app.route('/blogs')
def single_User():
    owner = request.args.get('user')
    user = User.query.filter_by(username=owner).first()
    blogs = Blog.query.filter_by(owner=user).all()
    return render_template('single_User.html', blogs=blogs, user=user)

@app.route('/blog', methods=['POST','GET'])
def blog():
        if request.method == 'GET':
            post_id = request.args.get('id')

            if type(post_id) == str:
                posts = Blog.query.get(post_id)
                return render_template('single_post.html', posts=posts)                
            else:
                posts = Blog.query.all()
                return render_template('blog.html', posts=posts)

        if request.method == 'POST':
            post_title = request.form['post-title']
            post_body = request.form['post-body']
            owner = User.query.filter_by(username=session['username']).first()
            if post_title == '':
                title_error = 'Enter title'
            else:
                title_error = ''
            if post_body == '':
                body_error = 'Enter body'
            else:
                body_error = ''

            if title_error == '' and body_error == '':
                new_post = Blog(post_title, post_body, owner)
                db.session.add(new_post)
                db.session.commit()
                id= str(new_post.id)
                return redirect('/blog?id=' + id)
            else:
                return render_template('new_posts.html', title_error=title_error, body_error=body_error)

if __name__ == '__main__':
    app.run()
