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

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
        #self.password_hash = pass_hash.decode("utf-8", "ignore")'

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'id':self.id})


    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = Users.query.get(data['id'])
        return user





@auth.verify_password
def verify_password(username_or_token, password):
    user = Users.verify_auth_token(username_or_token)
    if not user:
        user = Users.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/auth/register', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if Users.query.filter_by(username=username).first() is not None:
        abort(400)
    user = Users(username, password)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username':user.username}), 201,
            {'Location':url_for('get_user', id=user.id, _extername=True)})


@app.route('/auth/users/<int:id>')
def get_user(id):
    user = Users.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username':user.username})


@app.route('/auth/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token':token.decode('ascii'), 'duration':600})


@app.route('/auth/users/')
@auth.login_required
def get_resource():
    return jsonify({'data':'Hello, %s!' % g.user.username})


@app.route('/')
def index():
    return "<h1 style='color:red'>Hello there</h1>"

"""
@app.route('/post_user', methods=['POST'])
def post_user():
    user = Users(request.form['username'], request.form['name'],
                request.form['password'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token':token.decode('ascii')})
"""


if __name__ == "__main__":
    app.run()
