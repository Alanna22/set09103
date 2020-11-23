from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm
app = Flask(__name__)


app.config['SECRET_KEY'] = '9b8c9b04b07fea67ce7bccef71cdad88'

posts = [
    {

        'author': 'Alanna Craig',
        'title': 'Kickflip Help',
        'content': 'Help me kickflip',
        'date_posted': 'Nov 20, 2020'
        },
        {
        'author': 'Brooke Smith',
        'title': 'Love skating',
        'content': 'I love skating',
        'date_posted': 'Nov 21, 2020'
        }
            
]

@app.route('/')
@app.route('/home')
def home():
    regForm = RegistrationForm()
    loginForm = LoginForm()
    return render_template('home.html', title='Welcome', regForm=regForm, loginForm=LoginForm)

@app.route('/feed')
def feed():
    return render_template('feed.html', posts=posts)




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True) 
