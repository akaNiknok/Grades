import os
import json
from flask import Flask, render_template, request
from flask import redirect, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
import openpyxl
from openpyxl.utils import range_boundaries

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    acc_type = db.Column(db.String(11))

    firstname = db.Column(db.String())
    middlename = db.Column(db.String())
    lastname = db.Column(db.String())

    grade = db.Column(db.Integer)
    section = db.Column(db.String(4))
    CN = db.Column(db.Integer)

    subject = db.Column(db.String(7))
    sections = db.Column(db.String)

    def __init__(self,
                 username,
                 password,
                 acc_type,
                 firstname,
                 middlename,
                 lastname):
        self.username = username
        self.password = password
        self.acc_type = acc_type
        self.firstname = firstname
        self.middlename = middlename
        self.lastname = lastname

    def mi(self):
        """Returns middle initial of user"""
        mi = ""

        for name in self.middlename.split():
            mi += name[0]
            mi += "."

        return mi


db.create_all()


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":

        # Refresh for students
        user_id = request.cookies.get("user_id")
        user = User.query.get(user_id)
        subjects = read_excels(user.grade, user.section, user.CN)

        # Make response and create a cookie for subjects
        response = make_response(render_template("index.html",
                                                 user=user,
                                                 subjects=subjects))
        response.set_cookie("subjects", json.dumps(subjects))

        return response

    else:
        user_id = request.cookies.get("user_id")

        # Check if logged in
        if user_id:
            user = User.query.get(user_id)

            # Get subjects from cookies if user is student
            if user.acc_type == "student":

                # Get cookie of subjects
                subjects = request.cookies.get("subjects")

                # Load the subjects if it exists
                if subjects is not None:
                    subjects = json.loads(subjects)

                return render_template(
                    "index.html",
                    user=user,
                    subjects=subjects
                )

            # Get sections if user is teacher
            elif user.acc_type == "teacher":
                return render_template(
                    "index.html",
                    user=user,
                    sections=json.loads(user.sections)
                )

            # Get teachers if user is coordinator
            elif user.acc_type == "coordinator":
                return render_template(
                    "index.html",
                    user=user,
                    teachers=User.query.filter_by(
                        subject=user.subject,
                        acc_type="teacher"
                    ).all(),
                    loads=json.loads
                )
        else:
            user = None

        return render_template("index.html", user=user)


@app.route('/about')
def about():
    user_id = request.cookies.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

    return render_template("about.html", user=user)


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":

        # Get data from general forms
        username = request.form["username"]
        password = request.form["password"]
        re_password = request.form["re_password"]
        acc_type = request.form["acc_type"]

        firstname = request.form["firstname"]
        middlename = request.form["middlename"]
        lastname = request.form["lastname"]

        # Student Specific Forms
        grade = request.form["grade"]
        section = request.form["section"]
        CN = request.form["CN"]

        # Teacher Specific Forms
        new_teacher_pass = request.form["new_teacher_pass"]
        new_teacher_subject = request.form["new_teacher_subject"]

        # Coordinator Specific Forms
        new_coord_pass = request.form["new_coord_pass"]
        new_coord_subject = request.form["new_coord_subject"]

        # Check if username is taken
        if User.query.filter_by(username=username).first() is None:

            # Validate retype password
            if password == re_password:

                # Add grade, section and CN when account type is student
                if acc_type == "student":
                    student = User(username,
                                   password,
                                   acc_type,
                                   firstname,
                                   middlename,
                                   lastname)
                    student.grade = int(grade)
                    student.section = section
                    student.CN = int(CN)

                    db.session.add(student)

                # Add subject and section when account type is teacher
                elif (acc_type == "teacher" and
                        new_teacher_pass == "CSQC new teach"):
                    teacher = User(username,
                                   password,
                                   acc_type,
                                   firstname,
                                   middlename,
                                   lastname)
                    teacher.subject = new_teacher_subject
                    teacher.sections = "[]"
                    db.session.add(teacher)

                # Add subject when account type is coordinator
                elif (acc_type == "coordinator" and
                        new_coord_pass == "CSQC new coord"):
                    coord = User(username,
                                 password,
                                 acc_type,
                                 firstname,
                                 middlename,
                                 lastname)
                    coord.subject = new_coord_subject
                    db.session.add(coord)

                else:
                    return render_template("register.html", error=acc_type)

                db.session.commit()

            else:
                return render_template("register.html", error="password")
        else:
            return render_template("register.html", error="username")

        # Login new user if "All Izz Well" :D
        user = User.query.filter_by(username=username).first()
        response = make_response(redirect("/"))
        response.set_cookie("user_id", str(user.id))

        return response
    else:
        return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":

        # Get data from form
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        # Validate username
        if user is None:
            return render_template("login.html", error="username")

        # Validate password
        elif user.password == password:
            response = make_response(redirect("/"))
            response.set_cookie("user_id", str(user.id))
            return response
        else:
            return render_template("login.html", error="password")

    else:
        return render_template("login.html")


@app.route('/logout', methods=["GET"])
def logout():

    # Make response
    response = make_response(redirect("/"))

    # Set cookies to no value and expiration to the past :D
    response.set_cookie("user_id", "", expires=0)
    response.set_cookie("subjects", "", expires=0)

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


@app.route('/excels/<grade>/<section>/<subject>')
def excels(grade, section, subject):

    # Get user
    user_id = request.cookies.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

    return render_template("excel.html",
                           user=user,
                           grade=grade,
                           section=section,
                           subject=subject,
                           table=read_excel(grade, section, subject))


@app.route('/upload', methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        file = request.files['file']

        # Check if the file is present and is a spreadsheet (.xlsx, .xls)
        if file and (file.filename.endswith(".xlsx")
                     or file.filename.endswith(".xls")):

            # Get the user
            user_id = request.cookies.get("user_id")
            user = User.query.get(user_id)

            # Rename the file to subject.xlsx
            filename = user.subject + ".xlsx"

            # Directory for the excel file
            filedir = "excels/{}/{}/".format(request.form["grade"],
                                             request.form["section"])

            # Create Directory if it does not exist
            if not os.path.isdir(filedir):
                os.makedirs(filedir)

            # Save the file in the correct directory
            file.save(os.path.join(filedir, filename))

            sections = json.loads(user.sections)

            # Add the section to the list
            sections.append((request.form["grade"], request.form["section"]))

            # Save the list
            user.sections = json.dumps(sections)
            db.session.commit()

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
                return redirect("/")
        else:
            return redirect("/")


@app.route('/download/<grade>/<section>/<subject>')
def download(grade, section, subject):
    return send_file("excels/{}/{}/{}.xlsx".format(grade, section, subject),
                     as_attachment=True)


@app.route('/delete', methods=["POST"])
def delete():

    # Get user
    user_id = request.cookies.get("user_id")
    user = User.query.get(user_id)

    # Get index
    delete_index = int(request.form["delete_index"])

    # Load the sections list
    sections = json.loads(user.sections)
    section = sections[delete_index]

    # Remove the section from the list and delete the file
    sections.pop(delete_index)
    os.remove(
        "excels/{}/{}/{}.xlsx".format(section[0], section[1], user.subject)
    )

    # Save the list
    user.sections = json.dumps(sections)
    db.session.commit()

    return redirect("/")


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
    filedir = "excels/{}/{}/".format(grade, section)

    # Get all files (subjects) in file directory
    try:
        files = os.listdir(filedir)
    except OSError:
        return None

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


def read_excel(grade, section, subject):
    """Reads an excel file and returns a table list"""

    # Open excel file
    wb = openpyxl.load_workbook("excels/{}/{}/{}".format(grade,
                                                         section,
                                                         subject + ".xlsx"),
                                data_only=True)

    # Open the sheet (subject to change)
    ws = wb.worksheets[0]

    # Get boundaries (min_col, min_row, max_col, max_row) of merged_cells
    merged_cells = [range_boundaries(r) for r in ws.merged_cell_ranges]

    table = []

    # Loop through rows
    for row in range(5, ws.max_row):

        # Contains columns (value, colspan) here
        new_row = []

        # Create an iterator object to be able to skip merged cells
        columns = iter(range(1, ws.max_column))

        # Loop through columns
        for column in columns:

            # Get value of cell
            value = ws.cell(row=row, column=column).value

            # Check if the cell is not empty
            if value is not None:
                colspan = 1

                # Check if cell is merged
                for r in merged_cells:
                    if (r[0] == column) and (r[1] == row):
                        colspan += (r[2] - r[0])  # Add to colspan
                        break

                new_row.append((value, colspan))

                # If cell is merged, skip (colspan - 1) iterations
                if colspan != 1:
                    for x in range(colspan - 1):
                        next(columns)
            else:
                new_row.append(("", 1))

        table.append(new_row)

    return table


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)


# At World's End (POTC :stuck_out_tongue_closed_eyes::skull:)
