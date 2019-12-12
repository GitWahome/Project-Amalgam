from amalgam import app
from amalgam import db

db.create_all()
if __name__=="__main__":
    app.run(debug=True)