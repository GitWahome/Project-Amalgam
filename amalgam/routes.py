import os
import secrets

from PIL import Image
from amalgam import app, db, bcrypt
from amalgam.forms import RegistrationForm, LoginForm, UpdateAccountForm, NotebookForm, SupportResourceForm,BaseResourceForm
from amalgam.ml_algorithms import JaccardScore, preprocess, CosineScore
from amalgam.models import User, Notebook, SupportResource, BaseResource
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_ckeditor import upload_success, upload_fail
from flask import send_from_directory
from time import sleep
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request



@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    notebooks = Notebook.query.order_by(Notebook.date_posted.desc()).paginate(per_page=3, page=page)

    return render_template("home.html", notebooks = notebooks)

@app.route("/about")
def about():
    return render_template("/about.html", title = "ABOUT")

@app.route("/register", methods = ['GET', 'POST'])
def registration_form():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created for {form.username.data}. You can now log in.','success')
        return redirect(url_for('login_form'))
    return render_template("register.html",title = "Register",form = form)

@app.route("/login",methods = ['GET', 'POST'])
def login_form():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email= form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f"Invalid Credentials {form.email.data or 'User'}. Check email and/or password", "danger")


    return render_template("login.html",title = "Login", form =form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics/', picture_fn)
    output_size = (128,128)
    image_resized = Image.open(form_picture)
    image_resized.thumbnail(output_size)
    image_resized.save(picture_path)

    return picture_fn

@app.route('/account',methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.picture.data:
        picture_file = save_picture(form.picture.data)
        current_user.image_file = picture_file


    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for("account"))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename= f"profile_pics/{ current_user.image_file }")
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@app.route('/notebook/new', methods = ['GET', 'POST'])
@login_required
def new_notebook():
    form = NotebookForm()

    if form.validate_on_submit():

        notebook = Notebook(title=form.title.data, description = request.form.get('description'),author=current_user)

        db.session.add(notebook)
        db.session.commit()
        flash("Your notebook has been created!", 'success')
        return redirect(url_for('home'))
    return render_template('create_notebook.html',title = "New Notebook" ,form = form, legend = "New Notebook")


@app.route('/notebook/<notebook_id>')
def notebook(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)

    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id)
    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resource_form = SupportResourceForm()
    base_resource_form = BaseResourceForm()
    return render_template('notebook.html',title = notebook.title, notebook=notebook,
                           support_resource_form = support_resource_form,base_resource_form = base_resource_form ,
                           base_resources = base_resources, support_resources = support_resources)

@app.route('/notebook/<int:notebook_id>/update',  methods = ['GET', 'POST'])
@login_required
def update_notebook(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    if notebook.author != current_user:

        abort(403)
    form = NotebookForm()

    if form.validate_on_submit():
        notebook.title = form.title.data
        notebook.description = request.form.get('description')
        db.session.commit()
        flash("Your notebook has been updated!", "success")
        return redirect(url_for('notebook', notebook_id=notebook.id))
    elif request.method == 'GET':
        form.title.data = notebook.title
        form.description.data = notebook.description
    return render_template('create_notebook.html', title="Update Notebook", legend ="Update Notebook", form=form)




@app.route('/notebook/<int:notebook_id>/delete',  methods = ['POST'])
@login_required
def delete_notebook(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    if notebook.author != current_user:
        abort(403)
    db.session.delete(notebook)
    db.session.commit()
    flash("Your notebook has been deleted!", "success")
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_notebooks(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()

    notebooks = Notebook.query.filter_by(author=user)\
        .order_by(Notebook.date_posted.desc())\
        .paginate(per_page=3, page=page)

    return render_template("user_notebooks.html", notebooks = notebooks, user = user)




@app.route('/files/<path:filename>')
def uploaded_files(filename):
    path = '/amalgam/static/notebook_files/'
    return send_from_directory(path, filename)

    notebook = Notebook.query.get_or_404(notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id)
    support_resource_form = SupportResourceForm()
    return render_template('notebook.html', title=notebook.title,support_resource_form=support_resource_form,
                           notebook=notebook, support_resources=support_resources)

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    # Add more validations here
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join('/the/uploaded/directory', f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)  # return upload_success call




@app.route('/notebook/<int:notebook_id>/support/<int:support_resource_id>/update',  methods = ['GET', 'POST'])
@login_required
def update_support(support_resource_id, notebook_id):
    support_resource = SupportResource.query.get_or_404(support_resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)
    if notebook.author != current_user:

        abort(403)
    form = SupportResourceForm()

    if form.validate_on_submit():
        support_resource.title = form.title.data
        support_resource.content = request.form.get('content')

        bases = BaseResource.query.filter_by(notebook_id=notebook_id)
        base_texts = [text_from_html(base.title)+" "+text_from_html(base.content) for base in bases]
        base_texts = " ".join(base_texts)




        support_resource.relevance = CosineScore(base_texts, text_from_html(support_resource.title+" "+support_resource.content))

        db.session.commit()
        flash("Your Support Resource Has been updated!", "success")
        return redirect(url_for('notebook', notebook_id=notebook.id))
    elif request.method == 'GET':
        form.title.data = support_resource.title
        form.content.data = support_resource.content

    return render_template('create_resource.html', title="Update Support Resource", legend ="Update Support Resource", form=form)

@app.route('/notebook/<int:notebook_id>/base/<int:base_resource_id>/update',  methods = ['GET', 'POST'])
@login_required
def update_base(base_resource_id, notebook_id):
    base_resource = BaseResource.query.get_or_404(base_resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)

    if notebook.author != current_user:

        abort(403)
    form = BaseResourceForm()

    if form.validate_on_submit():
        base_resource.title = form.title.data
        base_resource.content = request.form.get('content')

        db.session.add(base_resource)
        db.session.commit()

        flash("Your Base Resource Has been updated!", "success")
        return redirect(url_for('notebook', notebook_id=notebook.id))
    elif request.method == 'GET':
        form.title.data = base_resource.title
        form.content.data = base_resource.content

    return render_template('create_resource.html',title="Update Base Resource", legend ="Update Base Resource", form=form)




def text_from_html(base_html):
    if not base_html:
        return "None"
    soup = BeautifulSoup(base_html, 'html.parser')
    texts = soup.findAll(text=True)

    return " ".join(texts)

@app.route('/notebook_support_resources/<int:notebook_id>',  methods = ['GET','POST'])
def add_support_resources(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)

    bases = BaseResource.query.filter_by(notebook_id=notebook_id)
    content = ""
    if request.form.get('content'):
        content = request.form.get('content')
    base_texts = [text_from_html(base.title) + " " + text_from_html(base.content) for base in bases]
    base_texts = " ".join(base_texts)

    new_support_resource = SupportResource(notebook_id=notebook_id , title=request.form.get('title'),complete= False, content = request.form.get('content'),
                                           relevance = CosineScore(base_texts, text_from_html(content+request.form.get('title'))))


    db.session.add(new_support_resource)
    db.session.commit()


    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(SupportResource.relevance)
    base_resource_form = BaseResourceForm()
    support_resource_form = SupportResourceForm()
    flash(f"New resource added!", "success")
    return render_template('notebook.html', title=notebook.title,
                           support_resource_form=support_resource_form, base_resource_form=base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)



@app.route('/notebook_base_resources/<int:notebook_id>',  methods = ['GET','POST'])
def add_base_resources(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    new_base_resource = BaseResource(notebook_id=notebook_id , title=request.form.get('title'),
                                               content = request.form.get('content'), complete= False)



    db.session.add(new_base_resource)
    db.session.add(notebook)
    db.session.commit()



    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(SupportResource.relevance.asc())
    base_resource_form = BaseResourceForm()
    support_resource_form = BaseResourceForm()
    flash(f"New resource added!", "success")
    return render_template('notebook.html', title = notebook.title,
                           support_resource_form = support_resource_form, base_resource_form=base_resource_form,
                           notebook=notebook, base_resources = base_resources, support_resources = support_resources)


@app.route('/notebook/<int:notebook_id>/support/<int:support_resource_id>/delete',  methods = ['GET','POST'])
@login_required
def delete_support_resource(notebook_id,support_resource_id):
    support_resource = SupportResource.query.get_or_404(support_resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)

    if notebook.author != current_user:
        abort(403)
    db.session.delete(support_resource)
    db.session.commit()
    flash("Support resource deleted!", "success")


    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(SupportResource.relevance.asc())

    base_resource_form = BaseResourceForm()
    support_resource_form = BaseResourceForm()
    return render_template('notebook.html', title=notebook.title,
                           support_resource_form=support_resource_form, base_resource_form=base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)


@app.route('/notebook/<int:notebook_id>/base/<int:base_resource_id>/delete',  methods = ['GET','POST'])
@login_required
def delete_base_resource(notebook_id, base_resource_id):
    base_resource = BaseResource.query.get_or_404(base_resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)

    if notebook.author != current_user:
        abort(403)
    db.session.delete(base_resource)
    db.session.commit()
    flash("Base resource deleted!", "success")


    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(SupportResource.relevance.asc())

    base_resource_form = BaseResourceForm()
    support_resource_form = BaseResourceForm()
    return render_template('notebook.html', title=notebook.title,
                           support_resource_form=support_resource_form, base_resource_form=base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)