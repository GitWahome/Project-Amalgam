from datetime import datetime
from amalgam import db, login_manager
from flask_login import UserMixin
from sqlalchemy import PickleType, Column

locals()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20),nullable = True, default = "default.png")
    password = db.Column(db.String(60), nullable = False)
    notebooks = db.relationship('Notebook', cascade='all, delete-orphan',backref = 'author', lazy = True)

    def __repr__(self):
        return f" User('{self.username}', '{self.email}''{self.image_file}')"

class Notebook(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(100), nullable=False, default = "Title")
    date_posted = db.Column(db.DateTime, nullable= False, default = datetime.utcnow)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    base_resources = db.relationship('BaseResource', cascade='all, delete-orphan', backref='Base', lazy=True)
    support_resources = db.relationship('SupportResource',cascade='all, delete-orphan', backref = 'Support', lazy = True)
    def __repr__(self):
        return f"Notebook: {self.title}, Date Posted: {self.date_posted}"

class BaseResource(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(100), nullable=False, default="Title")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notebook_id = db.Column(db.Integer, db.ForeignKey('notebook.id'), nullable=False)
    relevance = db.Column(db.Float(), nullable=False, default=0.00)
    content = db.Column(db.String(200), default = 'Fill in Content by Clicking Update Resource Below')
    complete = db.Column(db.Boolean)
    def __repr__(self):
        return f" Base resource {self.title}, Content: {self.content}"

class SupportResource(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(100), nullable=False, default="Title")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    relevance = db.Column(db.Float(), nullable=False, default=0.00)
    notebook_id = db.Column(db.Integer, db.ForeignKey('notebook.id'), nullable=False)
    content = db.Column(db.String(200), default ='Fill in Content by Clicking Update Resource Below')
    complete = db.Column(db.Boolean)
    def __repr__(self):
        return f" Support resource {self.title}, Content: {self.content}"
