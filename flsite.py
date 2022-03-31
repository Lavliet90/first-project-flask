from flask import Flask, render_template

app = Flask(__name__)

menu = ['Upload', 'First app', 'Contact']

@app.route('/')
def index():
    return render_template('index.html', menu=menu)


@app.route('/about')
def about():
    return render_template('about_site.html', title='About Site', menu=menu)


if __name__ == '__main__':
    app.run(debug=True)
