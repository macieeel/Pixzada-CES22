from email.policy import default

from sqlalchemy import ARRAY
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


user_group = db.Table('user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

trans_group = db.Table('trans_group',
    db.Column('trans_id', db.Integer, db.ForeignKey('transaction.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
    )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(150))
    nome = db.Column(db.String(150))
    sobrenome = db.Column(db.String(150))
    ismember = db.relationship('Group', secondary = user_group, backref = 'members')

# username.ismember.append(groupname)
# username.ismember retorna um dicionario de grupos q ele participa
# groupname.members retorna um dicionario de participantes do grupo
# username.ismember.remove(groupname) remove o usuario do grupo

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200))
    value = db.Column(db.Float)
    vpu = db.Column(db.Float)
    user_id = db.Column(db.Integer)
    createdAt = db.Column(db.DateTime(timezone = True),default = func.now())
    ofgroup = db.relationship('Group', secondary = trans_group, backref = 'gettransactions')