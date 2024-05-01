from flask import Flask, render_template, request, redirect, url_for, session
from secrets import token_hex
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://chris:sirhc@172.16.181.82/fp160'

engine = create_engine('mysql://chris:sirhc@172.16.181.82/fp160')
Session = sessionmaker(bind=engine)

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.Float, default=0)  # Add a grade column

    @staticmethod
    def generate_next_id():
        session = Session()
        last_student = session.query(Student).order_by(Student.account_id.desc()).first()
        session.close()
        if last_student:
            return last_student.account_id + 1
        else:
            return 100

    def __init__(self, name):
        self.name = name
        self.account_id = Student.generate_next_id()

class Teacher(db.Model):
    __tablename__ = 'teachers'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    answer = db.Column(db.Integer)

class Test(db.Model):
    __tablename__ = 'tests'

    test_id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(255))
    teacher_id = db.Column(db.Integer)
    questions = db.relationship('Question', secondary='test_questions', backref=db.backref('tests', lazy=True))

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'

    test_id = db.Column(db.Integer, db.ForeignKey('tests.test_id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), primary_key=True)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/test_create', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        test_name = request.form['test_name']
        teacher_id = session.get('user_id')  
        print("Teacher ID:", teacher_id) 
        selected_question_ids = request.form.getlist('selected_questions')
        
        if teacher_id is None:
            return "Error: Teacher ID not found. Please log in again."

        new_test = Test(test_name=test_name, teacher_id=teacher_id)  
        db.session.add(new_test)
        db.session.commit()

        for question_id in selected_question_ids:
            question = Question.query.get(int(question_id))  # Convert question_id to integer
            if question:
                new_test.questions.append(question)
        
        db.session.commit()

        return redirect(url_for('student_test'))
 
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
        return render_template('registration_success.html', account_id=new_student.account_id, account_type='student')
    else:
        new_teacher = Teacher(name=name)
        db.session.add(new_teacher)
        db.session.commit()
        return render_template('registration_success.html', account_id=new_teacher.account_id, account_type='teacher')

from flask import jsonify

@app.route('/submit_test', methods=['POST'])
def submit_test():
    student_answers = request.form
    student_id = session.get('user_id')

    if student_id is None:
        return "Error: Student ID not found. Please log in again."

    correct_answers = {}  # Dictionary to store correct answers for each question
    for question in Question.query.all():
        correct_answers[question.question_id] = question.answer

    print("Correct Answers:", correct_answers)  # Debugging: Print correct answers

    num_correct_answers = sum(student_answers.get(f'answer_{question_id}', '') == str(correct_answers.get(question_id)) for question_id in correct_answers)
    total_questions = len(correct_answers)
    score = num_correct_answers / total_questions * 100

    print("Number of Correct Answers:", num_correct_answers)  # Debugging: Print number of correct answers
    print("Total Questions:", total_questions)  # Debugging: Print total questions
    print("Score:", score)  # Debugging: Print calculated score

    # Update student's grade in the database
    student = Student.query.get(student_id)
    student.grade = score
    db.session.commit()

    return jsonify({'score': score})



@app.route('/login')
def render_login():
    return render_template('login.html')

app.secret_key = 'secret_key'
@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        account_number_str = request.form.get('account_number')
        
        if not account_number_str:
            return render_template('login.html', error='Account number is required')
        
        try:
            account_number = int(account_number_str)
        except ValueError:
            return render_template('login.html', error='Invalid account number')
        
        user = None
        if 1 <= account_number <= 9:
            user = Teacher.query.filter_by(account_id=account_number).first()
        elif 100 <= account_number <= 109:
            user = Student.query.filter_by(account_id=account_number).first()
        
        if user:
            session['user_id'] = user.account_id  # Store user_id in session
            if isinstance(user, Student):
                return redirect(url_for('student_test'))
            else:
                return redirect(url_for('create_test'))
        else:
            return render_template('login.html', error='User not found or invalid account number')

    return render_template('login.html')


@app.route('/student_test', methods=['GET', 'POST'])
def student_test():
    if request.method == 'POST':
        # Handle form submission
        student_answers = request.form
        student_id = session.get('user_id')

        print("Student ID from session:", student_id)  # Debugging: Print student ID

        if student_id is None:
            return "Error: Student ID not found in session. Please log in again."

        student = Student.query.get(student_id)
        if student:
            # Your existing code to calculate score and update grade
            correct_answers = {}  # Dictionary to store correct answers for each question
            for question in Question.query.all():
                correct_answers[question.question_id] = question.answer

            num_correct_answers = sum(student_answers.get(f'answer_{question_id}', '') == str(correct_answers.get(question_id)) for question_id in correct_answers)
            total_questions = len(correct_answers)
            score = num_correct_answers / total_questions * 100

            # Update student's grade in the database
            student.grade = score
            db.session.commit()

            return render_template('display_score.html', score=score)
        else:
            # Print student IDs from the database for debugging
            all_student_ids = [student.account_id for student in Student.query.all()]
            print("All student IDs:", all_student_ids)
            return "Error: Student not found."

    else:
        # Your existing code to render the student test page
        tests = Test.query.filter(Test.teacher_id != None).all()
        for test in tests:
            test.questions = Question.query.join(TestQuestion).filter(TestQuestion.test_id == test.test_id).all()
        return render_template('student_test.html', tests=tests)

def add_questions():
    question1 = Question(question='What is 1+1?', answer=2)
    question2 = Question(question='What is 1+2?', answer=3)
    question3 = Question(question='What is 1+3?', answer=4)
    question4 = Question(question='What is 1+4?', answer=5)
    question5 = Question(question='What is 1+5?', answer=6)
    question6 = Question(question='What is 1+6?', answer=7)
    question7 = Question(question='What is 1+7?', answer=8)
    question8 = Question(question='What is 1+8?', answer=9)
    question9 = Question(question='What is 1+9?', answer=10)
    question10 = Question(question='What is 1+10?', answer=11)

    with app.app_context():
        db.metadata.reflect(engine)
        db.metadata.drop_all(engine)
        db.metadata.create_all(engine)

        db.session.add_all([question1, question2, question3, question4, question5,
                            question6, question7, question8, question9, question10])
        db.session.commit()

if __name__ == '__main__':
    db.metadata.reflect(engine)
    db.metadata.drop_all(engine)
    db.metadata.create_all(engine)
    add_questions()

    app.run(debug=True)
