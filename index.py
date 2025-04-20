from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from secrets import token_hex
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask(__name__)
app.secret_key = token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)

# ----------------- MODELS -----------------

class Student(db.Model):
    __tablename__ = 'students'
    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.Float, default=0)

    student_tests = db.relationship('StudentTest', backref='student', lazy=True)

    def update_grade(self, score):
        self.grade = score
        db.session.commit()


class Teacher(db.Model):
    __tablename__ = 'teachers'
    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Test(db.Model):
    __tablename__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(255))
    teacher_id = db.Column(db.Integer)

    student_tests = db.relationship('StudentTest', backref='test', lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    answer = db.Column(db.String(255))
    testID = db.Column(db.Integer, db.ForeignKey('tests.test_id'))
    test = db.relationship('Test', backref='questions', lazy=True)


class StudentTest(db.Model):
    __tablename__ = 'student_tests'
    student_id = db.Column(db.Integer, db.ForeignKey('students.account_id'), primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.test_id'), primary_key=True)
    test_taken = db.Column(db.Boolean, default=False)



@app.route('/')
def index():
    return render_template('base.html')


@app.route('/create_test', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        print(request.form)
        test_name = request.form.get('testName')
        student_name = request.form.get('student_name')

        student = Student.query.filter_by(name=student_name).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        teacher_id = session.get('user_id')
        if not teacher_id:
            return redirect(url_for('login'))

        test = Test(test_name=test_name, teacher_id=teacher_id)
        db.session.add(test)
        db.session.commit()

        question_list = request.form.getlist('question[]')
        answer_list = request.form.getlist('answer[]')

        for q_text, a_text in zip(question_list, answer_list):
            question = Question(
                question=q_text,
                answer=a_text,
                testID=test.test_id
            )
            db.session.add(question)

        db.session.commit()

        return render_template('test_create.html')

    return render_template('create_test.html')


@app.route('/student_test', methods=['GET', 'POST'])
def student_test():
    student_id = session.get('user_id')
    if not student_id:
        return redirect(url_for('login'))

    student = Student.query.get(student_id)
    all_tests = Test.query.filter(~Test.student_tests.any(student_id=student_id, test_taken=True)).all()

    selected_test = None
    if request.method == 'POST':
        test_id = request.form.get('test_id')

        if test_id:
            selected_test = Test.query.options(joinedload(Test.questions)) \
                .filter_by(test_id=test_id).first()

        score = 0
        total = 0
        for question in selected_test.questions:
            submitted_answer = request.form.get(f'answer_{question.question_id}')
            if submitted_answer:
                total += 1
                if submitted_answer.strip().lower() == question.answer.strip().lower():
                    score += 1

        percent = (score / total) * 100 if total > 0 else 0
        student.update_grade(percent)

        student_test = StudentTest.query.filter_by(student_id=student_id, test_id=test_id).first()
        if student_test:
            student_test.test_taken = True
        else:
            student_test = StudentTest(student_id=student_id, test_id=test_id, test_taken=True)
            db.session.add(student_test)

        db.session.commit()

        return render_template('display_score.html', score=percent)


    test_id = request.args.get('test_id')
    if test_id:
        selected_test = Test.query.options(joinedload(Test.questions)) \
            .filter_by(test_id=test_id).first()

    return render_template('student_test.html', all_tests=all_tests, selected_test=selected_test)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_name = request.form.get('account_name', '').strip()
        student = Student.query.filter_by(name=account_name).first()
        teacher = Teacher.query.filter_by(name=account_name).first()

        if student:
            session['user_id'] = student.account_id
            session['role'] = 'student'
            return redirect(url_for('student_test')) 

        if teacher:
            session['user_id'] = teacher.account_id
            session['role'] = 'teacher'
            return render_template('test_create.html')

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html', error=None)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('Name', '').strip()
        role = request.form.get('account_type')

        if not name or not role:
            return render_template('register.html', error='Please fill out the form')

        if role == 'student':
            new_user = Student(name=name)
        else:
            new_user = Teacher(name=name)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', error=None)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
