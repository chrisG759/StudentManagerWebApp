from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Pennsylvania2004!@172.16.181.39/fp160'

db = SQLAlchemy(app)

# Define your database model for the 'questions' table
class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    # Add columns for other attributes of the questions table

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/student_test')
def student_test():
    return render_template('student_test.html')

@app.route('/test_create')
def create_test():
    # Fetch questions from the database
    questions = Question.query.all()  # Adjust the query as needed
    return render_template('test_create.html', questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
