from amalgam import app
from amalgam import db

db.create_all()
if __name__=="__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    app.run(debug=True)
