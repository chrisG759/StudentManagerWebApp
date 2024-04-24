from flask import Flask, render_template, request
from sqlalchemy import Table, text, engine, create_engine, MetaData, String, Integer, Column, Float
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
conn_str = "mysql://chris:sirhc@localhost/fp160"
engine = create_engine(conn_str, echo=True)
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Teacher(db.Model):
    __tablename__ = 'teachers'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
# Define your database model for the 'questions' table
class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    # Add columns for other attributes of the questions table
# Define Boat model
metadata = MetaData()
questions = Table('questions', metadata,
    Column('question_id', Integer, primary_key=True),
    Column('question', String(255)),
    Column('answer', int),
)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/test_create', )
def create_test(qustion_id):
    conn = engine.connect()
    boat = conn.execute(text("SELECT * FROM questions WHERE question_id = :question_id"), {'id': 'question_id'}).fetchone()
    conn.close()

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

@app.route('/student_test')
def student_test():
    return render_template('student_test.html')

@app.route('/test_create')
def create_test():
    return render_template('test_create.html')

if __name__ == '__main__':
    app.run(debug=True)
