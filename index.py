from flask import Flask, render_template, request, redirect, url_for, redirect, session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://chris:sirhc@172.16.181.39/fp160'
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
    question = db.Column(db.String(255))
    answer = db.Column(db.Integer)

class SelectedQuestion(db.Model):
    __tablename__ = 'selected_questions'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/test_create', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        selected_question_ids = request.form.getlist('selected_questions')
        for question_id in selected_question_ids:
            selected_question = SelectedQuestion(question_id=question_id)
            db.session.add(selected_question)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        questions = Question.query.all()
        return render_template('test_create.html', questions=questions)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_number = int(request.form['account_number'])
        
        # Check if the account number belongs to a student
        if 1 <= account_number <= 9:
            user = Student.query.filter_by(id=account_number).first()
        # Check if the account number belongs to a teacher
        elif 101 <= account_number <= 109:
            user = Teacher.query.filter_by(id=account_number).first()
        else:
            return render_template('login.html', error='Invalid account number')
        
        if user:
            session['user_id'] = user.id
            return redirect('/')  # Redirect to the homepage after successful login
        else:
            return render_template('login.html', error='User not found')
    else:
        return render_template('login.html')

@app.route('/')
def home():
    # Retrieve the logged-in user from the session
    user_id = session.get('user_id')
    if user_id:
        # Fetch user details from the database based on user_id
        user = Student.query.get(user_id) or Teacher.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        return redirect('/login')

@app.route('/student_test')
def student_test():
    return render_template('student_test.html')

if __name__ == '__main__':
    app.run(debug=True)

