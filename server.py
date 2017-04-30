from flask import Flask, render_template, request
from flask import redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
