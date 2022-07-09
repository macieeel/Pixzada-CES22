from flask import Blueprint, render_template, request, session, jsonify
from flask_login import login_required, current_user
from .models import Group, User, Transaction
from . import db
from flask_cors import cross_origin

views = Blueprint('views', __name__)


@views.route('/', methods = ['GET','POST'])
@login_required
def homepage():

    return render_template('home.html', user=current_user)


@views.route('/teste', methods=["POST"])
def teste():
    return 'Hello'






