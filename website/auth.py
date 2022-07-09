from tokenize import group
from venv import create
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from .models import User, Group, Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_session import Session

auth = Blueprint("auth", __name__)


@auth.route("/@me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(id=user_id).first()

    groups_array = []

    if(len(user.ismember) > 0):
        for i in range(len(user.ismember)):
            groups_array.append({"nome":user.ismember[i].nome, "id": user.ismember[i].id})

    saldo_groups = []
    for i in range(len(user.ismember)):
        saldo_groups.append(0)
        for j in range(len(user.ismember[i].gettransactions)):
            if user.ismember[i].gettransactions[j].user_id == user_id:
                    saldo_groups[i] += (user.ismember[i].gettransactions[j].value - user.ismember[i].gettransactions[j].vpu)
            else:
                saldo_groups[i] -= user.ismember[i].gettransactions[j].vpu

    return jsonify({
        "id": user.id,
        "nome": user.nome,
        "groups": groups_array,
        "saldo_groups": saldo_groups
    })

@auth.route("/groupsbyuser", methods=["GET"])
def usergroups():

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(id=user_id).first()
    groups_array = []
    if(len(user.ismember) > 0):
        for i in range(len(user.ismember)):
            groups_array.append({"nome":user.ismember[i].nome, "id": user.ismember[i].id})
    return jsonify({
        "groups": groups_array
    })

@auth.route("/rota")
def funcao():
    user_id = session.get("user_id")

    # if not user_id:
    #     return jsonify({"error": "Unauthorized"}), 401

    # user = User.query.filter_by(id=user_id).first()

    return jsonify({
        "id": user_id
    })


@auth.route("/login", methods=["POST"])
def login():

    email = request.json["email"]
    senha = request.json["senha"]

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not check_password_hash(user.senha, senha):
        return jsonify({"error": "Unauthorized"}), 401

    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "email": user.email
    })


@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id")
    return "200"


@auth.route("/signin", methods=["POST"])
def sign_up():
    email = request.json["email"]
    nome = request.json["nome"]
    sobrenome = request.json["sobrenome"]
    senha = request.json["senha1"]

    # User.query.delete()
    # db.session.commit()
    user = User.query.filter_by(email=email).first()
    
    if user is not None:
        return jsonify({"error": "User already exists"}), 409

    new_user = User(email=email, senha=generate_password_hash(senha, method="sha256"),
                    nome=nome, sobrenome=sobrenome)

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })

@auth.route("/makegroup", methods=["POST"])
def creategroup():

    gname = request.json["group_name"]
    uid = session.get("user_id")
    user = User.query.filter_by(id = uid).first()
    new_group = Group(nome = gname)
    db.session.add(new_group)
    user.ismember.append(new_group)
    
    emails_array = request.json["emails_array"]

    for useremail in emails_array:
        user = User.query.filter_by(email = useremail).first()
        user.ismember.append(new_group)

    db.session.commit()

    return jsonify({
        "nome": new_group.nome,
        "id": new_group.id

    })

@auth.route('/groupbyid/<gid>',methods=["GET"])
def getgroupbyid(gid):

    uid = session.get("user_id")
    user = User.query.filter_by(id = uid).first()
    grupo = Group.query.filter_by(id = gid).first()

    participants = [ ]
    for i in range(len(grupo.members)):
        if(grupo.members[i].nome != user.nome):
            participants.append({"nome": grupo.members[i].nome, "id": grupo.members[i].id})

    transactions = []
    for i in range(len(grupo.gettransactions)):
        nomeCreator = User.query.filter_by(id = grupo.gettransactions[i].user_id).first().nome
        transactions.append({
        "value": grupo.gettransactions[i].value,
        "valuePerUser": grupo.gettransactions[i].vpu,
        "description": grupo.gettransactions[i].comment,
        "createdAt": grupo.gettransactions[i].createdAt,
        "user": nomeCreator
    })

    saldos = []
    for i in range(len(participants)):
        saldos.append(0)

    for i in range(len(transactions)):
        if grupo.gettransactions[i].user_id == uid:
            for j in range(len(participants)):
                saldos[j] += grupo.gettransactions[i].vpu
        else:
            index = 0
            for j in range(len(participants)):
                if participants[j]["id"] == grupo.gettransactions[i].user_id:
                    index = j
                    break
            saldos[index] -= grupo.gettransactions[i].vpu
    
    return jsonify({
        "nome": grupo.nome,
        "id": grupo.id,
        "participants": participants,
        "transactions": transactions,
        "saldos": saldos
    })

@auth.route('/createtransaction/<gid>',methods=["POST"])
def createdespesa(gid):
    valor = request.json["value"]
    comment = request.json["description"]
    userCreator = User.query.filter_by(id = session.get("user_id")).first().nome
    grupo = Group.query.filter_by(id = gid).first()
    vpu = float(valor) / len(grupo.members)
    new_despesa = Transaction(comment = comment, value = valor, vpu = vpu, user_id = session.get("user_id"))
    new_despesa.ofgroup.append(grupo)
    db.session.add(new_despesa)
    db.session.commit()
    
    return jsonify({
        "value": valor,
        "valuePerUser": vpu,
        "description": comment,
        "createdAt": new_despesa.createdAt,
        "user": userCreator
    })

@auth.route('/paid/<gid>', methods=["DELETE"])
def deletetransaction(gid):
    user = User.query.filter_by(id = session.get("user_id")).first()
    group = Group.query.filter_by(id = gid).first()

    transObs = []
    for i in range(len(group.gettransactions)):
        transObs.append(group.gettransactions[i])
        #if group.gettransactions[i].user_id == user.id:
         #   group.gettransactions[i].ofgroup.remove(group)

    for i in range(len(group.gettransactions)):
        if transObs[i].user_id == user.id:
            transObs[i].ofgroup.remove(group)
            db.session.delete(transObs[i])
            db.session.commit()

    return jsonify({"success": "deleted"})


@auth.route('/addparticipants/add/<gid>', methods=["POST"])
def addMember(gid):

    group = Group.query.filter_by(id = gid).first()
    emails_array = request.json["emails_array"]
    for useremail in emails_array:
        user = User.query.filter_by(email = useremail).first()
        user.ismember.append(group)
    
    for i in range(len(group.gettransactions)):
        group.gettransactions[i].vpu = group.gettransactions[i].value / len(group.members)
        
    db.session.commit()
    return jsonify({"success": "Added new group members"})
