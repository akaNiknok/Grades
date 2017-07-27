import os
import json
from flask import Flask, render_template, request, session
from flask import redirect, make_response, send_file
from flask_mail import Mail, Message
from bs4 import BeautifulSoup
from read import read_html, read_htmls, read_excel, get_files, get_teacher
from models import db, User

# CONFIGS
app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)
mail = Mail(app)
HOSTNAME = os.getenv("HOSTNAME")


@app.before_first_request
def init_db():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def index():
    user_id = session.get("user_id")

    if request.method == "POST":

        # Refresh for students
        user = User.query.get(user_id)
        subjects = read_htmls(user.grade, user.section, user.CN)
        session["subjects"] = subjects

        return redirect("/")

    else:
        # Check if logged in
        if user_id:
            user = User.query.get(user_id)

            # Get subjects from session if user is student
            if user.acc_type == "student":
                return render_template(
                    "index.html.j2",
                    user=user,
                    subjects=session.get("subjects")
                )

            # Get children if user is parent
            elif user.acc_type == "parent":

                # Load children and create a new dict
                children = json.loads(user.children)
                new_children = {}

                # Loop through children
                for child in children:

                    # Get the user of child
                    child = User.query.filter_by(username=child,
                                                 activated=True).first()
                    new_children[child] = []

                    files = get_files(child.grade, child.section)

                    # Append subject to the list inside of the dict
                    for file in files:
                        if file.endswith(".j2"):
                            new_children[child].append(file.split(".")[0])

                return render_template(
                    "index.html.j2",
                    user=user,
                    children=new_children
                )

            # Get sections if user is teacher
            elif user.acc_type == "teacher":
                return render_template(
                    "index.html.j2",
                    user=user,
                    sections=json.loads(user.sections)
                )

            # Get teachers if user is coordinator
            elif user.acc_type == "coordinator":
                return render_template(
                    "index.html.j2",
                    user=user,
                    sections=json.loads(user.sections),
                    teachers=User.query.filter_by(
                        subject=user.subject,
                        acc_type="teacher",
                        activated=True
                    ).all(),
                    loads=json.loads
                )
        else:
            user = None

        return render_template("index.html.j2", user=user)


@app.route("/about")
def about():
    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

    return render_template("about.html.j2", user=user)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":

        # Get data from general forms
        email = request.form["email"]
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
        parent_username = request.form["parent_username"]
        parent_password = request.form["parent_password"]

        # Teacher Specific Forms
        new_teacher_pass = request.form["new_teacher_pass"]
        new_teacher_subject = request.form["new_teacher_subject"]

        # Coordinator Specific Forms
        new_coord_pass = request.form["new_coord_pass"]
        new_coord_subject = request.form["new_coord_subject"]

        # Check if email is taken
        if User.query.filter_by(email=email).first() is not None:
            return render_template("register.html.j2", error="email")

        # Check if username is taken
        elif User.query.filter_by(username=username).first() is not None:
            return render_template("register.html.j2", error="username")

        # Validate retype password
        elif password != re_password:
            return render_template("register.html.j2", error="password")

        # Signing up as student
        elif acc_type == "student":

            # Get parent user
            parent = User.query.filter_by(
                        username=parent_username
                    ).first()

            # Check if username and password of parent is correct
            if parent is None:
                return render_template("register.html.j2",
                                       error="parent-username")
            elif parent.password != parent_password:
                return render_template("register.html.j2",
                                       error="parent-password")

            # Create student
            student = User(email,
                           username,
                           password,
                           acc_type,
                           firstname,
                           middlename,
                           lastname)
            student.grade = int(grade)
            student.section = section
            student.CN = int(CN)

            # Add student to children list of parent
            children = json.loads(parent.children)
            children.append(username)
            parent.children = json.dumps(children)

            db.session.add(student)

        # Signing up as parent
        elif acc_type == "parent":

            # Create parent
            parent = User(email,
                          username,
                          password,
                          acc_type,
                          firstname,
                          middlename,
                          lastname)
            parent.children = "[]"

            db.session.add(parent)

        # Signing up as teacher
        elif (acc_type == "teacher" and
                new_teacher_pass == "CSQC new teach"):

            # Create teacher
            teacher = User(email,
                           username,
                           password,
                           acc_type,
                           firstname,
                           middlename,
                           lastname)
            teacher.subject = new_teacher_subject
            teacher.sections = "[]"
            db.session.add(teacher)

        # Signing up as coordinator
        elif (acc_type == "coordinator" and
                new_coord_pass == "CSQC new coord"):

            # Create coordinator
            coord = User(email,
                         username,
                         password,
                         acc_type,
                         firstname,
                         middlename,
                         lastname)
            coord.subject = new_coord_subject
            teacher.sections = "[]"
            db.session.add(coord)

        # Entered the wrong new_*_pass
        else:
            return render_template("register.html.j2", error=acc_type)

        # Save changes
        db.session.commit()

        # Email new user
        user = User.query.filter_by(username=username).first()
        msg = Message("Confirm Your Account on CSQC Grades",
                      sender=("CSQC Grades", "no.reply.grades@gmail.com"),
                      recipients=[email])
        msg.html = render_template("emails/email_activate.html.j2",
                                   HOSTNAME=HOSTNAME,
                                   username=username,
                                   email=email,
                                   id=user.id)
        mail.send(msg)

        return redirect("/activate")
    else:
        return render_template("register.html.j2")


@app.route("/activate")
def activate():

    email = request.args.get("email")
    id = request.args.get("id")

    # Check if user is coming from email
    if (email is None) or (id is None):
        return render_template("email_status.html.j2", status="registered")

    # Get user
    user = User.query.get(id)

    # Activate account if account is not yet activated
    if not user.activated:

        # Check email
        if email == user.email:
            user.activated = True
            db.session.commit()
            return render_template("email_status.html.j2", status="activated")

    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():

    # Get user
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    # Get index
    delete_index = int(request.form["delete_index"])

    # Load the sections list
    sections = json.loads(user.sections)
    section = sections[delete_index]

    # Remove the section from the list and delete the files
    sections.pop(delete_index)
    os.remove(
        "excels/{}/{}/{}.xlsx".format(section[0], section[1], user.subject)
    )
    os.remove(
        "excels/{}/{}/{}.html.j2".format(section[0], section[1], user.subject)
    )

    # Save the list
    user.sections = json.dumps(sections)
    db.session.commit()

    return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        # Get data from form
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        # Validate username
        if user is None:
            return render_template("login.html.j2", error="username")

        # Validate password
        elif user.password != password:
            return render_template("login.html.j2", error="password")

        # Check if user activated his accunt
        elif not user.activated:
            return render_template("login.html.j2", error="email")

        response = make_response(redirect("/"))
        session["user_id"] = user.id
        return response

    else:
        return render_template("login.html.j2")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/user/<username>", methods=["POST", "GET"])
def user(username):
    user_id = session.get("user_id")

    if request.method == "POST":

        # Get user
        user = User.query.get(user_id)

        # Check if user wants to change password or delete his/her account
        submit = request.form["submit"]

        if submit == "Change Password":

            # Get data from form
            orig_pass = request.form["orig_pass"]
            new_pass = request.form["new_pass"]
            re_new_pass = request.form["re_new_pass"]

            # Check if original password matches user's password
            if orig_pass != user.password:
                return render_template("user.html.j2",
                                       user=user,
                                       view_user=user,
                                       error="orig_pass")

            # Check if new password matches retype password
            elif new_pass != re_new_pass:
                return render_template("user.html.j2",
                                       user=user,
                                       view_user=user,
                                       error="re_new_pass")

            # Change the password and save to database
            else:
                user.password = new_pass
                db.session.commit()

                return render_template("user.html.j2",
                                       user=user,
                                       view_user=user,
                                       success=True)

        else:
            # Get data from form
            username = request.form["username"]
            password = request.form["password"]

            # Validate username
            if user.username != username:
                return render_template("user.html.j2",
                                       user=user,
                                       view_user=user,
                                       error="username")
            # Validate password
            elif user.password != password:
                return render_template("user.html.j2",
                                       user=user,
                                       view_user=user,
                                       error="password")

            else:
                # Logout and Delete account
                session.clear()
                db.session.delete(user)
                db.session.commit()

                return redirect("/")

    else:
        if user_id:
            user = User.query.get(user_id)

            # Check if logged in user is viewing his own account
            if user.username == username:
                view_user = user
            else:
                view_user = User.query.filter_by(username=username).first()
        else:
            user = None
            view_user = User.query.filter_by(username=username).first()

        return render_template("user.html.j2", user=user, view_user=view_user)


@app.route("/forgot", methods=["POST", "GET"])
def forgot_password():
    if request.method == "POST":

        submit = request.form["submit"]

        if submit == "email":
            email = request.form["email"]

            user = User.query.filter_by(email=email).first()

            # Check if account exists
            if user is None:
                return render_template("forgot.html.j2",
                                       status="forgot",
                                       error="email")

            # Check if account is activated
            elif user.activated is not True:
                return render_template("forgot.html.j2",
                                       status="forgot",
                                       error="activated")

            # Email the user
            msg = Message("Change Your Password on CSQC Grades",
                          sender=("CSQC Grades", "no.reply.grades@gamil.com"),
                          recipients=[email])
            msg.html = render_template("emails/email_forgot.html.j2",
                                       HOSTNAME=HOSTNAME,
                                       username=user.username,
                                       email=email,
                                       id=user.id)
            mail.send(msg)

            return render_template("email_status.html.j2", status="forgot")

        else:
            email = request.args.get("email")
            id = request.args.get("id")
            password = request.form["password"]
            re_password = request.form["re_password"]

            # Get user
            user = User.query.get(id)

            # Check email if it matches
            if email == user.email:

                # Validate password
                if password != re_password:
                    return render_template("forgot.html.j2",
                                           status="emailed",
                                           email=email,
                                           id=id,
                                           error="password")

                # Change the password and save to database
                user.password = password
                db.session.commit()

                return render_template("forgot.html.j2",
                                       status="success")

            return redirect("/")

    else:
        email = request.args.get("email")
        id = request.args.get("id")

        # Check if user is coming from email
        if (email is None) or (id is None):
            return render_template("forgot.html.j2", status="forgot")

        return render_template("forgot.html.j2",
                               status="emailed",
                               email=email,
                               id=id)


@app.route("/excels/<grade>/<section>/<subject>")
def excels(grade, section, subject):
    # Get user
    user_id = session.get("user_id")

    if user_id:
        user = User.query.get(user_id)
    else:
        return redirect("/")

    # Only allow teachers, parents and coordinators to view excels
    if user.acc_type not in ("teacher", "parent", "coordinator"):
        return redirect("/")

    # Read pre-rendered table
    with open("excels/{}/{}/{}".format(grade,
                                       section,
                                       subject + ".html.j2")) as f:
        soup = BeautifulSoup(f.read())

    # Read URL parameters
    fullscreen = request.args.get("fullscreen")
    cn = request.args.get("cn")

    if user.acc_type == "teacher" or user.acc_type == "coordinator":
        trimesters = {}

        for tag in soup.find_all("div"):
            if not fullscreen:
                trimesters[tag.get("id")] = tag
            else:
                trimesters[tag.get("id")] = tag.find("table")
    else:
        trimesters = read_html(grade, section, int(cn), soup)

    if not fullscreen:
        return render_template("excel.html.j2",
                               user=user,
                               grade=grade,
                               section=section,
                               subject=subject,
                               trimesters=trimesters)
    else:
        return render_template("fullscreen.html.j2",
                               user=user,
                               grade=grade,
                               section=section,
                               subject=subject,
                               trimesters=trimesters)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    user_id = session.get("user_id")

    if request.method == "POST":
        file = request.files['file']

        # Check if the file is present and is a spreadsheet (.xlsx, .xls)
        if file and (file.filename.endswith(".xlsx")
                     or file.filename.endswith(".xls")):

            # Get the user
            user = User.query.get(user_id)

            # Get data from forms
            grade = request.form["grade"]
            section = request.form["section"]

            # Rename the file to subject.xlsx and subject.html.j2
            filename = user.subject + ".xlsx"
            filename_j2 = user.subject + ".html.j2"

            # Directory for the excel file
            filedir = "excels/{}/{}/".format(grade, section)

            # If the file already exist, don't add anonther section to the list
            if not os.path.isfile(filedir + filename):
                sections = json.loads(user.sections)

                # Add the section as tuple to the list
                sections.append((grade, section))

                # Save the list
                user.sections = json.dumps(sections)
                db.session.commit()

            # Create Directory if it does not exist
            if not os.path.isdir(filedir):
                os.makedirs(filedir)

            # Save the file in the correct directory
            file.save(os.path.join(filedir, filename))

            # Read excel
            trimesters = read_excel(grade, section, user.subject)

            # Pre-render table and save to file
            with open(os.path.join(filedir, filename_j2), "w") as f:
                f.write(render_template("table.html.j2",
                                        trimesters=trimesters))

            return render_template("upload.html.j2", user=user, success=True)
        else:
            return render_template("upload.html.j2", user=user, error=True)

    else:

        # Require user to be a teacher or coordinator
        if user_id:
            user = User.query.get(user_id)
            if user.acc_type == "teacher" or "coordinator":
                return render_template("upload.html.j2", user=user)
            else:
                return redirect("/")
        else:
            return redirect("/")


@app.route("/download/<grade>/<section>/<subject>")
def download(grade, section, subject):
    return send_file("excels/{}/{}/{}.xlsx".format(grade, section, subject),
                     as_attachment=True,
                     attachment_filename=get_teacher(grade, section, subject)
                     + ".xlsx")


if __name__ == "__main__":
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.run(host="0.0.0.0", threaded=True)


# At World's End (POTC :stuck_out_tongue_closed_eyes::skull:)
