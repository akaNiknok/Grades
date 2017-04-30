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
    user_id = request.cookies.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

    return render_template("index.html", user=user)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":

        # Get data from forms
        username = request.form["username"]
        password = request.form["password"]
        re_password = request.form["re_password"]
        acc_type = request.form["acc_type"]

        # Validate retype password
        if password == re_password:

            # Check if username is taken
            if User.query.filter_by(username=username).first() is None:
                db.session.add(User(username, password, acc_type))
                db.session.commit()
            else:
                return render_template("register.html", error="username")
        else:
            return render_template("register.html", error="password")

        # Login new user
        user = User.query.filter_by(username=username).first()
        response = make_response(redirect(url_for("index")))
        response.set_cookie("user_id", str(user.id))

        return response
    else:
        return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user is None:
            return render_template("login.html", error=True)
        else:
            if user.password == password:
                response = make_response(redirect(url_for("index")))
                response.set_cookie("user_id", str(user.id))
                return response
            else:
                return render_template("login.html", error=True)

    else:
        return render_template("login.html")


@app.route('/logout', methods=["GET"])
def logout():
    response = make_response(redirect(url_for("index")))
    response.set_cookie("user_id", "")
    return response


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
