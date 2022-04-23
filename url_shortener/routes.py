from flask import render_template, url_for, flash, redirect, request, abort
import re
from url_shortener import app, db
from url_shortener.models import Url


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_to_short = (request.form['original']).lower()
        if not url_to_short.startswith("http"):
            url_to_short = f'http://{url_to_short}'
        regex = re.compile(
            r'^(?:http)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not re.match(regex, url_to_short):
            flash('Invalid URL!')
            return redirect(url_for('home'))
        url_exists = Url.query.filter_by(original_url=url_to_short).first()
        if url_exists:
            return render_template('index.html', short_url=f'{request.host_url}{url_exists.new_url}')
        url = Url(original_url=url_to_short.lower(), created_by=request.remote_addr)
        db.session.add(url)
        db.session.commit()
        return render_template('index.html', short_url=url)
    return render_template('index.html')


@app.route('/stats')
def stats():
    urls = Url.query.order_by(Url.hits.desc()).limit(50)
    return render_template('stats.html', urls=urls, host_url=request.host_url)


@app.route('/<path>', methods=['GET'])
def url_redirect(path):
    url = Url.query.filter_by(new_url=path.lower()).first()
    if url:
        url.hits += 1
        db.session.commit()
        return redirect(url.original_url)
    abort(404)


@app.errorhandler(404)
def page_not_found(e):
    flash('Page Not found! 404')
    return redirect(url_for('home'))
