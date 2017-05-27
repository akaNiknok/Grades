import os
from flask import Flask, render_template, request
from flask import redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import openpyxl

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


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":

        user_id = request.cookies.get("user_id")

        user = User.query.get(user_id)
        subjects = read_excels(user.grade, user.section, user.CN)

        return render_template("index.html", user=user, subjects=subjects)

    else:
        user_id = request.cookies.get("user_id")

        # Check if logged in
        if user_id:
            user = User.query.get(user_id)
        else:
            user = None

        return render_template("index.html", user=user, subjects=None)


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
            return render_template("login.html", error="username")
        else:
            if user.password == password:
                response = make_response(redirect(url_for("index")))
                response.set_cookie("user_id", str(user.id))
                return response
            else:
                return render_template("login.html", error="password")

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


@app.route('/upload', methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        file = request.files['file']

        # Check if the file is present and is a spreadsheet (.xlsx, .xls)
        if file and (file.filename.endswith(".xlsx")
                     or file.filename.endswith(".xls")):

            # Rename the file to subject.xlsx
            filename = request.form["subject"] + ".xlsx"

            # Directory for the excel file
            filedir = "excels/{}/{}/".format(request.form["grade"],
                                             request.form["section"])

            # Create Directory if it does not exist
            if not os.path.isdir(filedir):
                os.makedirs(filedir)

            file.save(os.path.join(filedir, filename))

            return render_template("upload.html", success=True)
        else:
            return render_template("upload.html", error=True)

    else:
        user_id = request.cookies.get("user_id")

        # Require user to be a teacher or coordinator
        if user_id:
            user = User.query.get(user_id)
            if user.acc_type == "teacher" or "coordinator":
                return render_template("upload.html", user=user)
            else:
                return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))


def read_excels(grade, section, cn):
    """Return format:
        subjects = {
            "Subject": {
                "Test": (int(Student Score), int(Total Score))
            }
        }
    """

    # Rows for label and total score
    TEST_LABEL_ROW = 7
    TEST_TOTAL_ROW = 8

    # Get file directory using users grade and section
    filedir = "excels/{}/{}/".format(grade,
                                     section)

    # Get all files (subjects) in file directory
    files = os.listdir(filedir)

    subjects = {}

    # Loop per subject
    for file in files:

        # Open the excel file
        wb = openpyxl.load_workbook(os.path.join(filedir, file),
                                    data_only=True)

        # Open the sheet (subject to change)
        ws = wb.worksheets[0]

        # Find CN rows
        for row in range(1, ws.max_row):
            if ws.cell(row=row, column=1).value == cn:
                user_row = row

        Tests = {}

        # Store tests in dictionary
        for col in range(3, ws.max_column):

            test_label = ws.cell(row=TEST_LABEL_ROW, column=col).value
            student_score = ws.cell(row=user_row, column=col).value
            total_score = ws.cell(row=TEST_TOTAL_ROW, column=col).value

            # Only include scores with label
            if ((test_label not in (None, "TS", "PS", "EP"))
                    and (student_score is not None)):

                if test_label in Tests:
                    Tests[test_label][0] += student_score
                    Tests[test_label][1] += total_score
                else:
                    Tests[test_label] = [student_score, total_score]

        # Store the tests in subject
        # Also removes the file extension
        subjects[os.path.splitext(file)[0]] = Tests

    return subjects


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)
