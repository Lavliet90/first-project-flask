from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
import sqlite3
import os

from UserLogin import UserLogin
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fwegwqg23r2fwr3r89jsfioejf29i2fjwlkjfq'
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Log in to access restricted pages'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


menu = [{'name': 'Upload', 'url': 'install-flask'},
        {'name': 'First app', 'url': 'first-app'},
        {'name': 'Contact', 'url': 'contact'}]


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route('/')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Error add post', category='error')
            else:
                flash('Success add page', category='success')
        else:
            flash('Error add post', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title='Add page')


@app.route('/post/<alias>')
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/about')
def about():
    print(url_for('about'))
    return render_template('about_site.html', title='About Site', menu=menu)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Invalid username/password pair', 'error')

    return render_template('login.html', title='Login', menu=dbase.getMenu())


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash('Yoy have successfully registered', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error add to db', 'error')
        else:
            flash('Fields filled out incorrectly', 'error')
    return render_template('register.html', menu=dbase.getMenu(), title='Registration')

    return render_template('register.html', menu=dbase.getMenu(), title='Registration')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Message sent!', category='success')
        else:
            flash('Error send!!!', category='error')

        print(request.form['username'])

    return render_template('contact.html', title='Contact', menu=menu)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logout', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<p><a href='{url_for('logout')}'>Sign out</a>
                <p>user info: {current_user.get_id()}"""


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title='Page not fount', menu=menu)


if __name__ == '__main__':
    app.run(debug=True)
