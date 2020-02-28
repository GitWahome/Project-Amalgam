from datetime import datetime
from amalgam import db, login_manager
from flask_login import UserMixin

locals()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique = True, nullable = False)
    email = db.Column(db.String(), unique = True, nullable = False)
    image_file = db.Column(db.String(),nullable = True, default = "default.png")
    password = db.Column(db.String(), nullable = False)
    api_key = db.Column(db.String(), nullable=False, default = 'acc_7a44f4db9a95430')
    api_secret  = db.Column(db.String(), nullable=False, default = '6ee0c5833ce2b25f280abbe77aa530cd')
    notebooks = db.relationship('Notebook', cascade='all, delete-orphan',backref = 'author', lazy = True)

    def __repr__(self):
        return f" User('{self.username}', '{self.email}''{self.image_file}')"

class Notebook(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(), nullable=False, default = "Title")
    date_posted = db.Column(db.DateTime, nullable= False, default = datetime.utcnow)
    description = db.Column(db.String())
    analytics = db.Column(db.String(), default='{}')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    base_resources = db.relationship('BaseResource', cascade='all, delete-orphan', backref='Base', lazy=True)
    support_resources = db.relationship('SupportResource',cascade='all, delete-orphan', backref = 'Support', lazy = True)
    def __repr__(self):
        return {"id":self.id,"title":self.title,"date_posted":str(self.date_posted),
                "description":self.description,"analytics":self.analytics,"user_id":self.user_id
                }

class BaseResource(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(), nullable=False, default="Title")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notebook_id = db.Column(db.Integer, db.ForeignKey('notebook.id'), nullable=False)
    relevance = db.Column(db.Float(), nullable=False, default=0.00)
    content = db.Column(db.String(), default = 'Fill in Content by Clicking Update Resource Below')
    analytics = db.Column(db.String(), default = '{}')
    is_pdf = db.Column(db.Boolean, default = False)
    pdf_url = db.Column(db.String(), default = 'NONE')
    def __repr__(self):
        return {"id":self.id,"title":self.title,"date_posted":str(self.date_posted),
                "notebook_id":self.notebook_id,"relevance":self.relevance, "content":self.content,
                "analytics":self.analytics,"is_pdf":self.is_pdf, "pdf_url":self.pdf_url
                }

class SupportResource(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(), nullable=False, default="Title")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    relevance = db.Column(db.Float(), nullable=False, default=0.00)
    notebook_id = db.Column(db.Integer, db.ForeignKey('notebook.id'), nullable=False)
    content = db.Column(db.String(), default ='Fill in Content by Clicking Update Resource Below')
    analytics = db.Column(db.String(), default='{}')
    is_pdf = db.Column(db.Boolean, default=False)
    pdf_url = db.Column(db.String(), default='NONE')
    def __repr__(self):
        return {"id":self.id,"title":self.title,"date_posted":str(self.date_posted),
                "notebook_id":self.notebook_id,"relevance":self.relevance, "content":self.content,
                "analytics":self.analytics,"is_pdf":self.is_pdf, "pdf_url":self.pdf_url
                }
