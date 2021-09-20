import random as rd
import string
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
import re
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)


class URL(db.Model):
    original = db.Column(db.String, primary_key=True)
    new = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"URL('{self.original}','{self.new}')"


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        x = (request.form['original']).lower()
        if not x.startswith("http"):
            x = f'http://{x}'
        regex = re.compile(
            r'^(?:http)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        original = URL.query.filter_by(original=x).first()
        letters = string.ascii_lowercase
        if not re.match(regex, x):
            flash('Invalid URL!')
            return redirect(url_for('home'))
        while True:
            short = ''.join(rd.choice(letters) for i in range(5))
            new = URL.query.filter_by(new=short.lower()).first()
            if not original and not new:
                url = URL(original=x.lower(), new=short.lower())
                short_url = f'{request.host_url}{short.lower()}'
                db.session.add(url)
                db.session.commit()
                print(short_url)
                break
            elif original:
                print("already exists", original)
                short_url = f'{request.host_url}{original.new}'
                break
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')


@app.route('/<id>', methods=['GET'])
def url_redirect(id):
    new = URL.query.filter_by(new=id.lower()).first()
    if new:
        return redirect(new.original)
    else:
        flash('Invalid URL')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()



