from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)




##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts=db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)

@app.route('/new-post', methods=["GET", "POST"])
def make_post():
    form=CreatePostForm()
    if form.validate_on_submit():

        body=request.form.get('body')
        title=request.form.get('title')
        author=request.form.get('author')
        subtitle=request.form.get('subtitle')
        img_url=request.form.get('img_url')
        date=datetime.datetime.now().date()
        new_post=BlogPost(title=title,subtitle=subtitle, author=author,body=body,img_url=img_url, date=date)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html",form=form)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit-post/<int:post_id>", methods=["GET","POST"])
def edit_post(post_id):
    post=BlogPost.query.get(post_id)

    #create a Post Form with post pre compiled field
    edit_form=CreatePostForm(title=post.title, subtitle=post.subtitle, date=post.date, img_url=post.img_url,
                             author=post.author, body=post.body)
    #once the form is "validated on submit", the fields for SQL database are inherited
    #please note that when it is made for the first time, the data are got from request
    if edit_form.validate_on_submit():
        post.body=edit_form.body.data
        post.title=edit_form.title.data
        post.author=edit_form.author.data
        post.subtitle=edit_form.subtitle.data
        post.img_url=edit_form.img_url.data
        post.date=datetime.datetime.now().date()
        db.session.commit()
        return redirect(url_for('show_post', index=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post=BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return f"<h1> Post {post_id} successfully deleted </h1>"

if __name__ == "__main__":
    app.run(debug=True, host="localhost",port="5000")