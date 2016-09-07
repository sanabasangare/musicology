from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Subgenre, User

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
APPLICATION_NAME = "Musicology App"


engine = create_engine('sqlite:///musicology.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Music Genres
# genre = {'name': 'Alternative', 'id': '1'}

# genres = [{'name': 'Alternative', 'id': '1'}, {'name':'Rock', 'id':'2'},{'name':'World Music', 'id':'3'}]


# Music SubGenres
# subgenres = [ {'name':'Folk Punk', 'description':'a subdivision of Alternative music', 'id':'1'},
# {'name':'Smooth Jazz','description':'a subdivision of Jazz music', 'id':'2'},
# {'name':'Calypso Music', 'description':'a subdivision of World music', 'id':'3'},
# {'name':'Alternative Rap', 'description':'a subdivision of Hip Hop music', 'id':'4'},
# {'name':'Rock & Roll', 'description':'a subdivision of Rock music', 'id':'5'} ]
# subgenres =  {'name':'Folk Punk'','description':'a subdivision of Alternative music'}
# subgenres = []



# Anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    """Render the login page"""
    return render_template('login.html', STATE=state)

# Google Connect
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'credentials': credentials, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

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


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# JSON APIs

@app.route('/genre/<int:genre_id>/subgenres/JSON')
def subgenresJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    subgenres = session.query(Subgenre).filter_by(
        genre_id=genre_id).all()
    return jsonify(Subgenres=[s.serialize for s in subgenres])

@app.route('/genre/<int:genre_id>/subgenres/<int:subgenre_id>/JSON')
def subgenreJSON(genre_id, subgenre_id):
    Subgenre = session.query(Subgenre).filter_by(id=subgenre_id).one()
    return jsonify(Subgenre=Subgenre.serialize)

@app.route('/genres/JSON')
@app.route('/musicology/JSON')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[g.serialize for g in genres])


# Show all music genres
@app.route('/')
@app.route('/genres/')
def showGenres():
    genres = session.query(Genre).all()
    if 'username' not in login_session:
        return render_template('public_genres.html', genres=genres)
    else:
    # return "This page shows all the music genres"
        return render_template('genres.html', genres=genres)


# Add a new genre
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGenre = Genre(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newGenre)
        flash('New Genre %s Successfully Created' % newGenre.name)
        session.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('newgenre.html')
    # return "This page is for adding a new genre"


# Edit a genre
@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    editedGenre = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedGenre.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to edit this genre. Please add a new music genre in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
            flash('Genre Successfully Edited %s' % editedGenre.name)
            return redirect(url_for('showGenres'))
    else:
        return render_template(
            'editgenre.html', genre=editedGenre)
    # return 'This page is for editing genre %s' % genre_id


# Delete a genre
@app.route('/genre/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    genreToDelete = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if genreToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this genre. Please create a genre in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(genreToDelete)
        flash('%s Successfully Deleted' % genreToDelete.name)
        session.commit()
        return redirect(
            url_for('showGenres', genre_id=genre_id))
    else:
        return render_template(
            'deletegenre.html', genre=genreToDelete)
    # return 'This page will be for deleting genre %s' % genre_id


# Show subgenres
@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/subgenres/')
def showSubgenres(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(genre.user_id)
    subgenres = session.query(Subgenre).filter_by(
        genre_id=genre_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_subgenres.html', subgenres=subgenres, genre=genre, creator=creator)
    else:
        return render_template('subgenre.html', subgenres=subgenres, genre=genre, creator=creator)
    # return 'This page shows the subgenres of genre %s' % genre_id


# Add a new subgenre
@app.route(
    '/genre/<int:genre_id>/subgenre/new/', methods=['GET', 'POST'])
def newSubgenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if login_session['user_id'] != genre.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add subgenres of this genre. Please add your own genre in order to add subgenres.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newSubgenre = Subgenre(name=request.form['name'], description=request.form[
                           'description'], genre_id=genre_id)
        session.add(newSubgenre)
        session.commit()
        flash('New Subgenre %s Successfully Created' % (newSubgenre.name))
        return redirect(url_for('showSubgenres', genre_id=genre_id))
    else:
        return render_template('newsubgenre.html', genre_id=genre_id)
    # return 'This page is for making a new subgenre for genre %s' %genre_id


# Edit a subgenre
@app.route('/genre/<int:genre_id>/subgenre/<int:subgenre_id>/edit',
           methods=['GET', 'POST'])
def editSubgenre(genre_id, subgenre_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedSubgenre = session.query(Subgenre).filter_by(id=subgenre_id).one()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if login_session['user_id'] != genre.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit the subgenres of this genre. Please add your own genre in order to add and edit subgenres.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedSubgenre.name = request.form['name']
        if request.form['description']:
            editedSubgenre.description = request.form['description']
        session.add(editedSubgenre)
        session.commit()
        flash('Subgenre Successfully Edited')
        return redirect(url_for('showSubgenres', genre_id=genre_id))
    else:
        return render_template(
            'editsubgenre.html', genre_id=genre_id, subgenre_id=subgenre_id, subgenre=editedSubgenre)

    # return 'This page is for editing subgenre %s' % subgenre_id


# Delete a subgenre
@app.route('/genre/<int:genre_id>/subgenre/<int:subgenre_id>/delete',
           methods=['GET', 'POST'])
def deleteSubgenre(genre_id, subgenre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    subgenreToDelete = session.query(Subgenre).filter_by(id=subgenre_id).one()
    if login_session['user_id'] != genre.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this subgenre. Please add your own genre in order to delete its subgenres.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(subgenreToDelete)
        session.commit()
        flash('Subgenre Successfully Deleted')
        return redirect(url_for('showSubgenre', genre_id=genre_id))
    else:
        return render_template('deletesubgenre.html', subgenre=subgenreToDelete)
    # return "This page is for deleting subgenre %s" % subgenre_id

# Disconnect user based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showGenres'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showGenres'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
