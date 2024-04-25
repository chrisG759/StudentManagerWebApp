from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://chris:sirhc@172.16.181.82/fp160'
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Teacher(db.Model):
    __tablename__ = 'teachers'

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255))
    answer = db.Column(db.Integer)

class SelectedQuestion(db.Model):
    __tablename__ = 'selected_questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer)


class Test(db.Model):
    __tablename__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100))

    # Define the relationship with Question using primaryjoin and secondaryjoin
    questions = db.relationship('Question', secondary='selected_questions',
                                primaryjoin="Test.test_id == SelectedQuestion.id",
                                secondaryjoin="SelectedQuestion.question_id == Question.question_id",
                                backref=db.backref('tests', lazy='dynamic'))


@app.route('/test_create', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        selected_question_ids = request.form.getlist('selected_questions')
        test_name = request.form.get('test_name')  # Assuming you have a field for test name in your form
        # Here you can create a new Test object and associate it with the selected questions
        new_test = Test(test_name=test_name)
        for question_id in selected_question_ids:
            question = Question.query.get(question_id)
            if question:
                new_test.questions.append(question)
        db.session.add(new_test)
        db.session.commit()
        return redirect(url_for('index'))  # Redirect to the homepage after saving the test
    else:
        questions = Question.query.all()
        return render_template('test_create.html', questions=questions)

# Other routes and functions remain unchanged

if __name__ == '__main__':
    app.run(debug=True)
