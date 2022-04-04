from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
import sqlite3
import os

from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fwegwqg23r2fwr3r89jsfioejf29i2fjwlkjfq'
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


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
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

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
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

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
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogger']))
    elif request.method == 'POST' and request.form['username'] == 'yan' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title='Log in', menu=menu)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Message sent!', category='success')
        else:
            flash('Error send!!!', category='error')

        print(request.form['username'])

    return render_template('contact.html', title='Contact', menu=menu)


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'User: {username}'


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title='Page not fount', menu=menu)


if __name__ == '__main__':
    app.run(debug=True)
