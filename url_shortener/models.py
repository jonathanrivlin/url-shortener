from random import choice
import string
from flask import request
from datetime import datetime

from url_shortener import db


class Url(db.Model):
    original_url = db.Column(db.String, primary_key=True)
    new_url = db.Column(db.String(120), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String, nullable=False)
    hits = db.Column(db.Integer, default=0)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.new_url = self.generate_new_url()

    def generate_new_url(self) -> str:
        characters = string.ascii_lowercase + string.digits
        new_url = ''.join(choice(characters) for _ in range(5))
        url_exists = Url.query.filter_by(new_url=new_url.lower()).first()
        if url_exists:
            return self.generate_new_url()
        return new_url

    def __repr__(self) -> str:
        return f"Url('{self.original_url}','{self.new_url}')"

    def __str__(self) -> str:
        return f'{request.host_url}{self.new_url}'
