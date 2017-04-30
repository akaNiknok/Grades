from flask import Flask, render_template, request
from flask import redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    acc_type = db.Column(db.String(7), nullable=False)

    def __init__(self, username, password, acc_type):
        self.username = username
        self.password = password
        self.acc_type = acc_type


db.create_all()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
