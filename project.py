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

''' Show all categories '''
@app.route('/')
@app.route('/categories')
def showCategories():
    #return "All Categories and descriptions"
    categories = session.query(Categories).all()
    return render_template('categories.html', categories = categories)

''' Create a new categorie '''
@app.route('/categories/new', methods=['GET', 'POST'])
def newCategorie():
    #return "Add new categorie"
    if request.method == 'POST':
        newCategorie = Categories(title=request.form['name'], 
        	description=request.form['description'])
        session.add(newCategorie)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategorie.html')

''' Edit a categorie '''
@app.route('/categories/<int:categorie_id>/edit', methods=['GET', 'POST'])
def editCategorie(categorie_id):
	# return "EditCategorie WORK! %s" % categorie_id
	editedCategorie = session.query(Categories).filter_by(id=categorie_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedCategorie.title = request.form['name']
		if request.form['description']:
			editedCategorie.description = request.form['description']
		session.add(editedCategorie)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('editcategorie.html', categorie_id=categorie_id, categorie=editedCategorie)

''' Delete a categorie '''
@app.route('/categories/<int:categorie_id>/delete', methods=['GET', 'POST'])
def deleteCategorie(categorie_id):
	# return "DeleteCategorie WORK! %s" % categorie_id
	categorieToDelete = session.query(Categories).filter_by(id=categorie_id).one()
	if request.method == 'POST':
		session.delete(categorieToDelete)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('deletecategorie.html', categorie=categorieToDelete, categorie_id=categorie_id)


''' Show a categorie items '''
@app.route('/categories/<int:categorie_id>/items')
def categorieItems(categorie_id):
    #return "Categorie ITEMS WORK! %s" % categorie_id
    categorie = session.query(Categories).filter_by(id=categorie_id).one()
    items = session.query(CategorieItem).filter_by(categorie_id=categorie_id)
    return render_template(
        'categorieitem.html', categorie=categorie, items=items, categorie_id=categorie_id)

''' Create a new categorie - item '''
@app.route('/categories/<int:categorie_id>/items/new', methods=['GET', 'POST'])
def newCategorieItem(categorie_id):
    #return "NewCategorieItem WORK! %s" % categorie_id
    categorie = session.query(Categories).filter_by(id=categorie_id).one()
    items = session.query(CategorieItem).filter_by(categorie_id=categorie_id)
    if request.method == 'POST':
        newItem = CategorieItem(title=request.form['name'], description=request.form[
                           'description'], categorie_id=categorie_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('categorieItems', categorie=categorie, items=items, categorie_id=categorie_id))
    else:
        return render_template('newitem.html', categorie_id=categorie_id, categorie=categorie)


''' Edit a categorie - item '''
@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editCategorieItem(item_id):
	#return "EditCategorieItem WORK! %s %s" % (categorie_id, item_id)
	editedItem = session.query(CategorieItem).filter_by(id=item_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.title = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		return redirect(url_for('categorieItems', categorie_id=editedItem.categorie_id))
	else:
		return render_template('edititem.html', categorie_id=editedItem.categorie_id, item_id=item_id, item=editedItem)

''' Delete a categorie - item '''
@app.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategorieItem(item_id):
	#return "DeleteCategorieItem WORK! %s %s" % (categorie_id, item_id)
	itemToDelete = session.query(CategorieItem).filter_by(id=item_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('categorieItems', categorie_id=itemToDelete.categorie_id))
	else:
		return render_template('deleteitem.html', item=itemToDelete, item_id=itemToDelete.id)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)