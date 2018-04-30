from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import cgi
import flask

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:test@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text(560))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title

@app.route('/newpost', methods=['POST', 'GET'])
def index():
        if request.method == 'GET':
            return render_template('new_posts.html')

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

        if post_title == '':
            title_error = 'Title is required'
        else:
            title_error = ''
        if post_body == '':
            body_error = 'Body is required'
        else:
            body_error = ''

        if title_error == '' and body_error == '':
            new_post = Blog(post_title, post_body)
            db.session.add(new_post)
            db.session.commit()
            id= str(new_post.id)
            return redirect('/blog?id=' + id)
        else:
            return render_template('new_posts.html', title_error=title_error, body_error=body_error)

if __name__ == '__main__':
    app.run()
