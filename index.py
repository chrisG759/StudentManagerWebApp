from flask import Flask, render_template
from sqlalchemy import table, text

app = Flask(__name__)

@app.route('/')

def index():
    return render_template('base.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login.html')
def login ():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)