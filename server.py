import os
from flask import Flask, render_template, request
from flask import redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    acc_type = db.Column(db.String(11))

    grade = db.Column(db.Integer)
    section = db.Column(db.String(4))
    CN = db.Column(db.Integer)

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

        # Student Specific
        grade = request.form["grade"]
        section = request.form["section"]
        CN = request.form["CN"]

        # Teacher and Coordinator Specific
        new_teacher_pass = request.form["new_teacher_pass"]
        new_coord_pass = request.form["new_coord_pass"]

        # Check if username is taken
        if User.query.filter_by(username=username).first() is None:

            # Validate retype password
            if password == re_password:

                # Add Grade, Section and CN when account type is Student
                if acc_type == "student":
                    student = User(username, password, acc_type)
                    student.grade = int(grade)
                    student.section = section
                    student.CN = int(CN)

                    db.session.add(student)

                # Check new teacher password
                elif (acc_type == "teacher" and
                        new_teacher_pass == "CSQC new teach"):
                    db.session.add(User(username, password, acc_type))

                # Check new coordinator password
                elif (acc_type == "coordinator" and
                        new_coord_pass == "CSQC new coord"):
                    db.session.add(User(username, password, acc_type))

                else:
                    return render_template("register.html", error=acc_type)

                db.session.commit()

            else:
                return render_template("register.html", error="password")
        else:
            return render_template("register.html", error="username")

        # Login new user if "All Izz Well" :D
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


@app.route('/user/<username>')
def user(username):
    user_id = request.cookies.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

    view_user = User.query.filter_by(username=username).first()

    return render_template("user.html", user=user, view_user=view_user)


@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['file']

    # Check if the file is present and is a spreadsheet (.xlsx)
    if file and (file.filename.rsplit('.', 1)[1] == "xlsx"):

        # Rename the file to subject.xlsx
        filename = request.form["subject"] + ".xlsx"

        # Directory for the excel file
        filedir = "excels/{}/{}/".format(request.form["grade"],
                                         request.form["section"])

        # Create Directory if it does not exist
        if not os.path.isdir(filedir):
            os.makedirs(filedir)

        file.save(os.path.join(filedir, filename))

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
