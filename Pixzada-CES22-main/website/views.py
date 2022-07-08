from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import Group, User, Transaction
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods = ['GET','POST'])
@login_required
def homepage():

    return render_template('home.html', user=current_user)

@views.route('/teste', methods=["POST"])
def teste():
    return 'Hello'

@views.route('/creategroup', methods=["POST"])
def creategroup():
    gname = request.json["groupname"]
    new_group = Group(nome = gname)

    useremail = request.json["useremail"]
    user = User.query.filter_by(email = useremail).first()
    user.ismember.append(new_group)
    return 200

@views.route('/despesa',methods=["POST"])
def createdespesa():
    valor = request.json["valor"]
    comment = request.json["Comment"]
    new_despesa = Transaction(value = valor, comment = comment, user_id = current_user.id, group_id = current_group)

    return 200

@views.route('/groups',methods=["POST"])

def getgroupsbyuser(user):
    grouplist = []
    for group in user.ismember:
        grouplist.append(group)

    return render_template('home.html', user=current_user)

@views.route('/getgroup',methods=["POST"])
def getgroupbyid():
    id = request.json["id"]
    return Group.query.get(id)

