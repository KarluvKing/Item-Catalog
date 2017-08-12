from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, CategorieItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories')
def Categories():
    return "Categories WORK!"

@app.route('/newcategorie')
def NewCategorie():
    return "NewCategorie WORK!"

@app.route('/editcategorie')
def EditCategorie():
    return "EditCategorie WORK!"

@app.route('/deletecategorie')
def DeleteCategorie():
    return "DeleteCategorie WORK!"

@app.route('/newcategorieitem')
def NewCategorieItem():
    return "NewCategorieItem WORK!"

@app.route('/editcategorieitem')
def EditCategorieItem():
    return "EditCategorieItem WORK!"

@app.route('/deletecategorieitem')
def DeleteCategorieItem():
    return "DeleteCategorieItem WORK!"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)