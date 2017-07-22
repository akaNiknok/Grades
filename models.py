from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    acc_type = db.Column(db.String(11))
    activated = db.Column(db.Boolean)

    firstname = db.Column(db.String())
    middlename = db.Column(db.String())
    lastname = db.Column(db.String())

    grade = db.Column(db.Integer)
    section = db.Column(db.String(4))
    CN = db.Column(db.Integer)

    children = db.Column(db.String)

    subject = db.Column(db.String(7))
    sections = db.Column(db.String)

    def __init__(self,
                 email,
                 username,
                 password,
                 acc_type,
                 firstname,
                 middlename,
                 lastname):
        self.email = email
        self.username = username
        self.password = password
        self.acc_type = acc_type
        self.firstname = firstname
        self.middlename = middlename
        self.lastname = lastname
        self.activated = False

    def mi(self):
        """Returns middle initial of user"""
        mi = " "

        if self.middlename != "":
            for name in self.middlename.split():
                mi += name[0]
                mi += "."
            mi += " "

        return mi
