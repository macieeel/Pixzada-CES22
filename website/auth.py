from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_session import Session

auth = Blueprint("auth", __name__)


@auth.route("/@me")
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(id=user_id).first()

    return jsonify({
        "id": user.id,
        "nome": user.nome
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
