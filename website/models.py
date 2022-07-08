from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


user_group = db.Table('user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

user_user = db.Table('user_user',
            db.Column('reciever_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('payer_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('transaction_id', db.Float, db.ForeignKey('transaction.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    nome = db.Column(db.String(150))
    sobrenome = db.Column(db.String(150))

    ismember = db.relationship('Group', secondary = user_group, backref = 'members')

    isreciever = db.relationship('User', secondary = user_user, backref = 'payer')

# username.ismember.append(groupname)
# username.ismember retorna um dicionario de grupos q ele participa
# groupname.members retorna um dicionario de participantes do grupo
# username.ismember.remove(groupname) remove o usuario do grupo

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    transactions = db.relationship('Transaction')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200))
    value = db.Column(db.Float)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer,db.ForeignKey('group.id'))