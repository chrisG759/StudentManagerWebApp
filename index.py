from flask import Flask, render_template, request
from sqlalchemy import Table, text, engine, create_engine, MetaData, String, Integer, Column, Float
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
conn_str = "mysql://chris:sirhc@localhost/fp160"
engine = create_engine(conn_str, echo=True)

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
    boat = conn.execute(text("SELECT * FROM questions WHERE question_id = :question_id"), {'id': question_id}).fetchone()
    conn.close()

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['Name']
    account_type = request.form['account_type']  # Get the selected account type

    # Create a new User object with the provided data
    new_user = User(name=name, account_type=account_type)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return 'User registered successfully!'

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
