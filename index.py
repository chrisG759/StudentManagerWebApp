from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Pennsylvania2004!@localhost/fp160'
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Teacher(db.Model):
    __tablename__ = 'teachers'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    name = request.form['Name']
    account_type = request.form['account_type']  

    if account_type == 'student':
        new_student = Student(name=name)
        db.session.add(new_student)
        db.session.commit()
        return 'Student registered successfully!'
    else:
        new_teacher = Teacher(name=name)
        db.session.add(new_teacher)
        db.session.commit()
        return 'Teacher registered successfully!'

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)