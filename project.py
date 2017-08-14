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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

''' Show all categories '''
@app.route('/')
@app.route('/categories')
def showCategories():
    #return "All Categories and descriptions"
    categories = session.query(Categories).all()
    return render_template('categories.html', categories = categories)

''' Show a categorie in JSON Format '''
@app.route('/categories/JSON')
def categoriesJSON():
	categories = session.query(Categories).all()
	return jsonify(Categories=[i.serialize for i in categories])

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

''' Show a categorie items in JSON Format '''
@app.route('/categories/<int:categorie_id>/items/JSON')
def categoriesItemsJSON(categorie_id):
	categorie = session.query(Categories).filter_by(id=categorie_id).one()
	items = session.query(CategorieItem).filter_by(categorie_id=categorie_id)
	return jsonify(CategorieItem=[i.serialize for i in items])

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
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)