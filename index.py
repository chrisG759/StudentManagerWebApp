from flask import Flask, render_template, request
from sqlalchemy import table, text
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Pennsylvania2004!@localhost/fp160'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('base.html')

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
def login ():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)