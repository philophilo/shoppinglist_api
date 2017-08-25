from flask import Flask, request, redirect, url_for, jsonify, g, abort
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as
                          Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://shopper:shop123@localhost/shopping_list'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


db = SQLAlchemy(app)
auth = HTTPBasicAuth()
class Users(db.Model):
    __tablename__ = 'users'
    password_hash = db.Column(db.String(200))
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(80))
    password = db.Column(db.String(64))


    def __init__(self, username, password, name="philo philo"):
        self.username = username
        self.name = name
        self.password = password

    def __repr__(self):
        return '<Users %r>' % self.username


if __name__ == "__main__":
    app.run()
