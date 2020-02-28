import os
import secrets

from PIL import Image
from amalgam import app, db, bcrypt
from amalgam.forms import RegistrationForm, LoginForm, UpdateAccountForm, NotebookForm, SupportResourceForm, \
    BaseResourceForm, AddPDFForm, NewSupportResourceForm, NewBaseResourceForm, AddJSONForm
from amalgam.ml_algorithms import JaccardScore, preprocess, CosineScore, neural_classifier, online_neural_classifier, \
    word_mover, text_distance
from amalgam.models import User, Notebook, SupportResource, BaseResource
from amalgam.pdfchunker import page_by_page_extract
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_ckeditor import upload_success, upload_fail
from flask import send_from_directory
from bs4 import BeautifulSoup
from base64 import b64decode, b64encode
from io import BytesIO
import json



@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    notebooks = Notebook.query.order_by(Notebook.date_posted.desc()).paginate(per_page=10, page=page)

    return render_template("home.html", notebooks=notebooks)


@app.route("/guides")
def guides():
    return render_template("guides.html", title="GUIDES")


def validate_notebook_json(notebook_json):
    return notebook_json is not ""

@app.route("/upload_notebook", methods=['GET', 'POST'])
def upload_notebook():
    form = AddJSONForm()
    if form.file.data:
        uploaded_json = str(form.file.data.read().decode("utf-8"))
        print("Uploaded JSON", uploaded_json)
        uploaded_json = json.loads(uploaded_json)

        if validate_notebook_json(uploaded_json):
            notebook = Notebook(title=uploaded_json['title'], description=uploaded_json['description'], author=current_user)
            db.session.add(notebook)
            db.session.commit()
            for base in list(uploaded_json['base_resources'].values()):
                print("Base",base)
                new_base_resource = BaseResource(notebook_id=notebook.id, title=base['title'],
                                                 is_pdf=base['is_pdf'], content=base['content'], analytics=base['analytics'])
                db.session.add(new_base_resource)
            for support in list(uploaded_json['support_resources'].values()):
                new_support_resource = SupportResource(notebook_id=notebook.id, title=support['title'],
                                                 is_pdf=support['is_pdf'], content=support['content'], analytics=support['analytics'])
                db.session.add(new_support_resource)
            db.session.commit()
            flash("Your notebook has been uploaded!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Invalid JSON, check format is correct.",'warning')

    return render_template("upload_notebook.html" , form = form, title="UPLOAD NOTEBOOK")

@app.route('/uploaded/save', methods=['GET', 'POST'])
@login_required
def save_uploaded_notebook():
    flash("SAVED", 'success')
    form = AddJSONForm()
    return render_template("upload_notebook.html", form = form, title="UPLOAD NOTEBOOK")

@app.route("/register", methods=['GET', 'POST'])
def registration_form():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created for {form.username.data}. You can now log in.', 'success')
        return redirect(url_for('login_form'))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login_form():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f"Invalid Credentials {form.email.data or 'User'}. Check email and/or password", "danger")

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_file(form_file, file_type):
    random_hex = secrets.token_hex(8)
    _, extension = os.path.splitext(form_file.filename)
    file_name = random_hex + extension
    paths = {
        'pdf_base': 'static/notebook_files/base',
        'pdf_support': 'static/notebook_files/support',
        'account_picture': 'static/profile_pics/'
    }
    save_path = paths[file_type]
    file_path = os.path.join(app.root_path, save_path, file_name)
    output_size = (64, 64)
    if file_type == "account_picture":
        file_resized = Image.open(form_file)
        file_resized.thumbnail(output_size)
        file_resized.save(file_path)
        res_url = url_for('static', filename=f"profile_pics/{file_name}")
    else:
        form_file.save(file_path)
        if file_type == 'pdf_base':
            res_url = url_for('static', filename=f"notebook_files/base/{file_name}")
        elif file_type == 'pdf_support':
            res_url = url_for('static', filename=f"notebook_files/support/{file_name}")

    return file_name, res_url


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.picture.data:
        picture_file, _ = save_file(form.picture.data, file_type='account_picture')
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

    image_file = url_for('static', filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Account", image_file=image_file, form=form)


@app.route('/notebook/new', methods=['GET', 'POST'])
@login_required
def new_notebook():
    form = NotebookForm()

    if form.validate_on_submit():
        notebook = Notebook(title=form.title.data, description=request.form.get('description'), author=current_user)

        db.session.add(notebook)
        db.session.commit()
        flash("Your notebook has been created!", 'success')
        return redirect(url_for('home'))
    return render_template('create_notebook.html', title="New Notebook", form=form, legend="New Notebook")

def generate_json(notebook):
    def Merge(dict1, dict2):
        dict2.update(dict1)
        return dict2


    file_url = os.path.join(app.root_path, 'static/notebook_files/generated/json/', f'{ notebook.id}.json')
    f = open(file_url, 'w+')
    full_json = {}
    full_json = Merge(full_json,{'support_resources':{}})
    full_json = Merge(full_json,{'base_resources':{}})

    full_json = Merge(full_json,notebook.__repr__())
    base_resources = BaseResource.query.filter_by(notebook_id=notebook.id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook.id)

    for base in base_resources:
        full_json['base_resources'][base.id] = base.__repr__()

    for support in support_resources:
        full_json['support_resources'][support.id] = support.__repr__()

    f.write(json.dumps(full_json))
    f.close()
    return url_for('static', filename = f"notebook_files/generated/json/{notebook.id}.json")

@app.route('/notebook/<notebook_id>')
def notebook(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)

    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id)
    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)

    new_support_resource_form = NewSupportResourceForm()
    new_base_resource_form = NewBaseResourceForm()
    notebook_json_file = generate_json(notebook)
    return render_template('notebook.html', notebook_json_file=notebook_json_file, title=notebook.title, notebook=notebook,
                           new_support_resource_form=new_support_resource_form,
                           new_base_resource_form=new_base_resource_form,
                           base_resources=base_resources, support_resources=support_resources)


@app.route('/notebook/<int:notebook_id>/update', methods=['GET', 'POST'])
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
    return render_template('create_notebook.html', title="Update Notebook", legend="Update Notebook", form=form)


@app.route('/notebook/<int:notebook_id>/delete', methods=['POST'])
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

    notebooks = Notebook.query.filter_by(author=user) \
        .order_by(Notebook.date_posted.desc()) \
        .paginate(per_page=3, page=page)

    return render_template("user_notebooks.html", notebooks=notebooks, user=user)





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


@app.route('/update_relevance/<notebook_id>')
@login_required
#TODO: The refresh functionality needs thorough reevaluation.
def update_relevance(notebook_id):
    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id)
    base_texts = " ".join(
        [content_processor(base.title, resource_identity=f"Base {base.id}-{base.title},") + " " +
         content_processor(base.content,resource_identity=f"Base {base.id}-{base.title},") for base in base_resources])
    for support_resource in support_resources:
        support_resource.relevance = CosineScore(base_texts, content_processor(
            support_resource.title + " " + support_resource.content,
            resource_identity=f"Support {support_resource.id}-{support_resource.title},"))
    notebook = Notebook.query.get_or_404(notebook_id)

    new_support_resource_form = NewSupportResourceForm()
    new_base_resource_form = NewBaseResourceForm()
    notebook_json_file = generate_json(notebook)
    return render_template('notebook.html', title=notebook.title, notebook=notebook, notebook_json_file= notebook_json_file,
                           new_support_resource_form=new_support_resource_form, new_base_resource_form=new_base_resource_form,
                           base_resources=base_resources, support_resources=support_resources)


@app.route('/notebook/<int:notebook_id>/support/<int:resource_id>/update', methods=['GET', 'POST'])
@login_required
def update_support(resource_id, notebook_id, page_split = 500):
    support_resource = SupportResource.query.get_or_404(resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)
    if notebook.author != current_user:
        abort(403)
    form = SupportResourceForm()
    form2 = AddPDFForm()

    if form.validate_on_submit():
        support_resource.title = form.title.data
        support_resource.content = request.form.get('content')
        support_resource.is_pdf = False

        bases = BaseResource.query.filter_by(notebook_id=notebook_id)
        analytics = eval(support_resource.analytics)
        for base in bases:
            base_text = content_processor(base.title,resource_identity=f"Base {base.id}-{base.title},") + " " +\
                        content_processor(base.content, resource_identity=f"Base {base.id}-{base.title},")
            base_text = " ".join(base_text)

            string_content = str(support_resource.content).split(" ")
            page_split = min(page_split, len(string_content))


            text_object = list([" ".join(string_content[pages - 500:pages]) for pages in
                           range(500, len(string_content), page_split)])

            analytics[base.title] = {str(page): {"Cosine Similarity": CosineScore(base_text, text_object[page]),
                                                 "Word Mover": word_mover(base_text, text_object[page]),
                                                 "Text Distance": text_distance(base_text, text_object[page]),
                                                 "Jaccard Similarity": JaccardScore(base_text, text_object[page])
                                      }
                             for page in range(len(text_object))}

        support_resource.analytics = str(analytics)

        db.session.commit()
        flash("Your Support Resource Has been updated!", "success")
        return redirect(url_for('notebook', notebook_id=notebook.id))
    elif request.method == 'GET':
        form.title.data = support_resource.title
        form.content.data = support_resource.content
    return render_template('create_resource.html', notebook_id=notebook.id, res_type="SUPPORT",
                           is_pdf=support_resource.is_pdf,
                           res_id=support_resource.id, form2=form2, legend="Update Support Resource", form=form)

@app.route('/notebook/<int:notebook_id>/base/<int:resource_id>/update', methods=['GET', 'POST'])
@login_required
def update_base(resource_id, notebook_id, page_split = 500):
    base_resource = BaseResource.query.get_or_404(resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)

    if notebook.author != current_user:
        abort(403)
    form = BaseResourceForm()
    form2 = AddPDFForm()
    if form.validate_on_submit():
        base_resource.title = form.title.data
        base_resource.content = request.form.get('content')
        #get full base_resource
        full_base_text = content_processor(base_resource.title+base_resource.content,
                                           resource_identity=f"Base {base_resource.id}-{base_resource.title},")
        #retrieve_all_support resources
        supports = SupportResource.query.filter_by(notebook_id=notebook_id)
        analytics = {}
        for support in supports:
            page_split = min(page_split, len(support.content))

            text_object = [" ".join(support.content[pages - 500:pages]) for pages in
                           range(500, len(support.content), page_split)]
            for page in range(len(text_object)):
                page_content= content_processor(text_object[page],
                                                resource_identity=f"Base {base_resource.id}-{base_resource.title}," )
                scores_object = {
                    "Jaccard Similarity":JaccardScore(full_base_text,page_content),
                    "Word Mover": word_mover(full_base_text, page_content),
                    "Text Distance": text_distance(full_base_text, page_content),
                    "Cosine Similarity":CosineScore(full_base_text,page_content)
                }
                analytics[f"Support Resource {support.id}"] = {page:scores_object}



        analytics = str(analytics)

        base_resource.analytics = analytics
        base_resource.is_pdf = False


        db.session.add(base_resource)
        db.session.commit()

        flash("Your Base Resource Has been updated!", "success")
        return redirect(url_for('notebook', notebook_id=notebook.id))
    elif request.method == 'GET':
        form.title.data = base_resource.title
        form.content.data = base_resource.content
    return render_template('create_resource.html', notebook_id=notebook.id, res_type="BASE", res_id=base_resource.id,
                           is_pdf=base_resource.is_pdf,
                           form2=form2, title="Update Base Resource", legend="Update Base Resource", form=form)


@app.route('/notebook/<int:notebook_id>/dedicated_view/<string:res_type>/<int:res_id>', methods=['GET', 'POST'])
@login_required
def dedicated_view(notebook_id, res_type, res_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    if res_type == 'BASE':
        main_resource = BaseResource.query.get_or_404(res_id)
        update_url = "update_base"
        delete_url = "delete_base_resource"
        res_name = "Base Resource"
        relevance_object = None
        analytics_metrics = []
        jaccard_scores, cosine_scores, pages = [], [], []


    elif res_type == "SUPPORT":
        main_resource = SupportResource.query.get_or_404(res_id)
        update_url = "update_support"
        delete_url = "delete_support_resource"
        res_name = "Support Resource"

        relevance_object = main_resource.analytics
        eval_ro = eval(relevance_object)
        analytics_metrics = list(eval_ro[next(iter(eval_ro))]['0'])
        print("Analytics Metrics", analytics_metrics)




    return render_template('dedicated_view.html', notebook=notebook, delete_url=delete_url, update_url=update_url,
                           relevance_object = relevance_object, analytics_metrics = analytics_metrics,
                           base_resources = base_resources,  main_resource=main_resource, res_name = res_name)


@app.route('/notebook_pdf_resources/<string:res_type>/<int:notebook_id>/<res_id>', methods=['GET', 'POST'])
def update_pdf_resources(res_type, notebook_id, res_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    form2 = AddPDFForm()
    if notebook.author != current_user:
        abort(403)
    if res_type == "BASE":
        modified = BaseResource.query.get_or_404(res_id)
        form = BaseResourceForm()
    elif res_type == "SUPPORT":
        modified = SupportResource.query.get_or_404(res_id)
        form = SupportResourceForm()

    if res_type == 'BASE':
        res_path = 'pdf_base'
    elif res_type == "SUPPORT":
        res_path = 'pdf_support'

    if form2.file.data:
        _, pdf_file_url = save_file(form2.file.data, res_path)
        modified.is_pdf = True
        modified.content = pdf_file_url

    if request.method == 'GET':
        form2.title.data = modified.title
        form.title.data = modified.title
        form.content.data = modified.content
        form.title.data = modified.title

    if form2.validate_on_submit:
        modified.title = form2.title.data
        bases = BaseResource.query.filter_by(notebook_id=notebook_id)
        print(modified.analytics)
        analytics = eval(modified.analytics)
        text_object = page_by_page_extract('amalgam' + modified.content)
        for base in bases:
            base_text = content_processor(base.title, resource_identity=f"Base {base.id}") +" " + \
                        content_processor(base.content,resource_identity=f"Base {base.id}-{base.title},")

            analytics[base.title] = {str(page): {"Cosine Similarity": CosineScore(base_text, text_object[page]),
                                                 "Word Mover": word_mover(base_text, text_object[page]),
                                                 "Text Distance": text_distance(base_text, text_object[page]),
                                                "Jaccard Similarity": JaccardScore(base_text, text_object[page])}
                                        for page in range(len(text_object))}

        modified.analytics = str(analytics)
        db.session.add(modified)
        db.session.commit()

        flash(f"Resource updated!", "success")
        return redirect(url_for("notebook", notebook_id=notebook_id))

    return render_template("create_resource.html", title="Account", notebook_id=notebook_id, is_pdf=modified.is_pdf,
                           res_type=res_type, res_id=res_id, form=form, form2=form2)


def handle_bytes(bytecode,size):
    image_code = bytes(bytecode, 'utf-8')
    image = b64decode(image_code)
    image = Image.open(BytesIO(image))
    image = image.resize(size)
    image = image.convert('RGB')
    return image, bytecode



def images_decoder(image_code,resource_identity, size=(299, 299)):
    try:
        _, image_bytecode = image_code.split(",")
        return handle_bytes(image_bytecode, size)
    except:
        flash(f"Analysis of Image {image_code} in {resource_identity} unsupported. Upload it directly into the editor for it to be analyzed.",
              "warning")
        return None, None






def content_processor(base_html, resource_identity):
    if not base_html:
        return "None"

    soup = BeautifulSoup(base_html, 'html.parser')
    texts = soup.findAll(text=True)
    images = soup.findAll('img')
    image_analytics = []
    imagga_string = ""
    for image in images:
        raw_image, image_data = images_decoder(image['src'], resource_identity)
        if raw_image and image_data:
            buffered = BytesIO()
            raw_image.save(buffered, format="JPEG")
            base_64 = b64encode(buffered.getvalue())
            imagga = online_neural_classifier(base_64, current_user)
            imagga_string = ",".join([str(rows["Classification"]+",")*int(abs(rows["Probability"])//10) for _, rows in imagga.iterrows()])
            print("Imagga String",imagga_string)
            image_analytics.append(neural_classifier(raw_image))

    return " ".join(texts)+imagga_string+",".join(image_analytics)



@app.route('/notebook_support_resources/<int:notebook_id>', methods=['GET', 'POST'])
def add_support_resources(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    bases = BaseResource.query.filter_by(notebook_id=notebook_id)
    if request.form.get('content'):
        content = request.form.get('content')
    else:
        content = "Fill in Content by Clicking Update Resource Below"


    new_support_resource = SupportResource(notebook_id=notebook_id, title=request.form.get('title'),
                                           is_pdf=False, content=content, analytics = "{}")
    db.session.add(new_support_resource)
    full_support = content_processor(content + request.form.get('title'),
                                     resource_identity=f"{new_support_resource.id}-{new_support_resource.title},")
    for base in bases:
        base_text = content_processor(base.title, resource_identity=f"base {base.id}-{base.title},") + " " + \
                    content_processor(base.content,resource_identity=f"base {base.id}-{base.title},")
        base_analytics = eval(base.analytics)
        base_analytics[f"Support Resource {new_support_resource.id}"] = \
            {"Jaccard Similarity":JaccardScore(full_support, base_text),
             "Word Mover": word_mover(full_support, base_text),
             "Text Distance": text_distance(full_support, base_text),
             "Cosine Similarity":CosineScore(full_support, base_text)}
        base.analytics = str(base_analytics)


    db.session.commit()

    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(SupportResource.relevance)
    new_base_resource_form = NewBaseResourceForm()
    new_support_resource_form = NewSupportResourceForm()
    notebook_json_file = generate_json(notebook)
    flash(f"New resource added!", "success")
    return render_template('notebook.html', title=notebook.title, notebook_json_file = notebook_json_file,
                           new_support_resource_form=new_support_resource_form,
                           new_base_resource_form=new_base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)


@app.route('/notebook_base_resources/<int:notebook_id>', methods=['GET', 'POST'])
def add_base_resources(notebook_id):
    notebook = Notebook.query.get_or_404(notebook_id)
    supports = SupportResource.query.filter_by(notebook_id=notebook_id)
    if request.form.get('content'):
        content = request.form.get('content')
    else:
        content = "Fill in Content by Clicking Update Resource Below"

    new_base_resource = BaseResource(notebook_id=notebook_id, title=request.form.get('title'),
                                     is_pdf=False, content = content, analytics = "{}")
    db.session.add(new_base_resource)
    full_base = content_processor(new_base_resource.content + new_base_resource.title,
                                  resource_identity=f"base {new_base_resource.id}-{new_base_resource.title},")
    print("Base Resource Analytics", new_base_resource.analytics)
    base_analytics = eval(new_base_resource.analytics)
    for support in supports:
        full_support = content_processor(support.title, resource_identity=f"Support {support.id}-{support.title},") +\
                       " " + content_processor(support.content,resource_identity=f"Support {support.id}-{support.title},")
        base_analytics[f"Support Resource {support.id}"] = \
            {"Jaccard Similarity": JaccardScore(full_support,full_base ),
             "Word Mover": word_mover(full_support, full_base),
             "Text Distance": text_distance(full_support, full_base),
             "Cosine Similarity": CosineScore(full_support, full_base)
             }

    new_base_resource.analytics = str(base_analytics)
    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(
        SupportResource.relevance.asc())
    new_base_resource_form = NewBaseResourceForm()
    new_support_resource_form = NewSupportResourceForm()
    flash(f"New resource added!", "success")


    db.session.add(notebook)
    db.session.commit()
    notebook_json_file = generate_json(notebook)
    return render_template('notebook.html', title=notebook.title, notebook_json_file = notebook_json_file,
                           new_support_resource_form=new_support_resource_form,
                           new_base_resource_form=new_base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)


@app.route('/notebook/<int:notebook_id>/support/<int:resource_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_support_resource(notebook_id, resource_id):
    support_resource = SupportResource.query.get_or_404(resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)

    if notebook.author != current_user:
        abort(403)

    db.session.delete(support_resource)
    db.session.commit()
    flash("Support resource deleted!", "success")

    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    for base in base_resources:
        base_analytics = eval(base.analytics)
        #del base_analytics[f'Support Resource {support_resource.id}']
        base.analytics = str(base_analytics)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(
        SupportResource.relevance.asc())

    new_base_resource_form = NewBaseResourceForm()
    new_support_resource_form = NewBaseResourceForm()
    notebook_json_file = generate_json(notebook)
    return render_template('notebook.html', title=notebook.title, notebook_json_file=notebook_json_file,
                           new_support_resource_form=new_support_resource_form,
                           new_base_resource_form=new_base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)


@app.route('/notebook/<int:notebook_id>/base/<int:resource_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_base_resource(notebook_id, resource_id):
    base_resource = BaseResource.query.get_or_404(resource_id)
    notebook = Notebook.query.get_or_404(notebook_id)

    if notebook.author != current_user:
        abort(403)
    db.session.delete(base_resource)
    db.session.commit()
    flash("Base resource deleted!", "success")

    base_resources = BaseResource.query.filter_by(notebook_id=notebook_id)
    support_resources = SupportResource.query.filter_by(notebook_id=notebook_id).order_by(
        SupportResource.relevance.asc())

    new_base_resource_form = BaseResourceForm()
    new_support_resource_form = BaseResourceForm()
    notebook_json_file = generate_json(notebook)
    return render_template('notebook.html', title=notebook.title,notebook_json_file=notebook_json_file,
                           new_support_resource_form=new_support_resource_form,
                           new_base_resource_form=new_base_resource_form,
                           notebook=notebook, base_resources=base_resources, support_resources=support_resources)


@app.route('/save_api_key', methods=['GET', 'POST'])
@login_required
def save_api_key():
    form = UpdateAccountForm()
    if form.picture.data:
        picture_file, _ = save_file(form.picture.data, file_type='account_picture')
        current_user.image_file = picture_file

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    print("Account Get Data:", request.args.get)
    new_key = request.args.get("api_key")
    new_secret = request.args.get("api_secret")
    if new_key == "Create immaga account and paste key here" or new_secret == "Create immaga account and paste secret here":
        flash("Update your Imagga Key and Password", "warning")
    else:
        if new_key:
            current_user.api_key = new_key
            flash("Imagga API Key updated", "success")

        else:
            flash("Check that your key is correct", "warning")
        if new_secret:
            current_user.api_secret = new_secret

            flash("Imagga API secret updated", "success")
        else:
            flash("Check that your secret is correct", "warning")
    if form.validate_on_submit():
        db.session.commit()


    image_file = url_for('static', filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Account", image_file=image_file, form=form)


