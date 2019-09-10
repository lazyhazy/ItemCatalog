import cgi
import random
import string
import httplib2
import json
import requests
from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, make_response, flash
from flask import session as login_session
from database_setup import Base, Catalog, CatalogItem, User
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from flask import make_response


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
USER_ID = None

engine = create_engine(
                'sqlite:///catalogmenu.db',
                connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/catalog/login', methods=['GET'])
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    redirect_url = request.args.get('redirect_url', default='None')
    return render_template(
                    'login.html', STATE=login_session['state'],
                    redirect_url=redirect_url)


@app.route('/')
@app.route('/catalog/')
def catalogMenu():
    catalog = session.query(Catalog).all()
    catalogitem = session.query(CatalogItem).all()
    sortedArray = sorted(
                    catalogitem,
                    key=lambda
                    x: datetime.strptime(str(
                                    x.datecreated), '%Y-%m-%d %H:%M:%S.%f'),
                    reverse=True)
    return render_template(
                    'mainmenu.html', catalog=catalog,
                    login_session=login_session,
                    sortedItem=sortedArray)


@app.route('/catalog/<int:catalog_id>/items')
def catalogItemList(catalog_id):
    catalog = session.query(Catalog).all()
    catalogitem = session.query(CatalogItem).filter_by(
                                                catalog_id=catalog_id).all()
    return render_template(
                    'catalogitemmenu.html', catalog=catalog,
                    catalog_id=catalog_id, catalogitem=catalogitem,
                    login_session=login_session)


@app.route('/catalog/<int:catalog_id>/new', methods=['GET', 'POST'])
def newCatalogItem(catalog_id):
    if 'username' not in login_session:
        redirect_url = "/catalog/"+str(catalog_id)+"/new"
        return redirect('/catalog/login?redirect_url='+redirect_url)
    USER_ID = getUserID(login_session['email'])
    if USER_ID is None:
        USER_ID = createUser(login_session)
    if request.method == 'POST':
        newCatalogItem = CatalogItem(
                        name=request.form['name'],
                        description=request.form['description'],
                        catalog_id=catalog_id,
                        user_id=USER_ID)
        session.add(newCatalogItem)
        flash('New CatalogItem- %s Successfully Created' % newCatalogItem.name)
        session.commit()
        return redirect(url_for('catalogItemList', catalog_id=catalog_id))
    else:
        return render_template(
                            'newcatalogitem.html', catalog_id=catalog_id,
                            login_session=login_session)


@app.route(
        '/catalog/<int:catalog_id>/<int:catalogitem_id>/edit',
        methods=['GET', 'POST'])
def editCatalogItem(catalog_id, catalogitem_id):
    if 'username' not in login_session:
        redirect_url = "/catalog/"+str(catalog_id)+"/"+str(
                                                    catalogitem_id)+"/edit"
        return redirect('/catalog/login?redirect_url='+redirect_url)

    USER_ID = getUserID(login_session['email'])
    editedcatalogitem = session.query(CatalogItem).filter_by(
                                                    id=catalogitem_id).one()
    if editedcatalogitem.user_id != USER_ID:
        return redirect('/catalog/unauthorisederror')
    if request.method == 'POST':
        if request.form['name']:
            editedcatalogitem.name = request.form['name']
        if request.form['description']:
            editedcatalogitem.description = request.form['description']
        if request.form['catalog_name']:
            selectedcatalog = request.form['catalog_name']
            catalog = session.query(Catalog).filter_by(
                                                    name=selectedcatalog).one()
            editedcatalogitem.catalog_id = catalog.id

        session.add(editedcatalogitem)
        flash('Catalog Item Successfully Edited %s' % editedcatalogitem.name)
        session.commit()
        return redirect(url_for('catalogItemList', catalog_id=catalog.id))
    else:
        catalog = session.query(Catalog).all()
        return render_template(
                        'editcatalogitem.html', catalog_id=catalog_id,
                        catalog=catalog, catalogitem=editedcatalogitem,
                        login_session=login_session)


@app.route('/catalog/<int:catalog_id>/<int:catalogitem_id>/view')
def viewCatalogItem(catalog_id, catalogitem_id):
    viewcatalogitem = session.query(CatalogItem).filter_by(
                                                    id=catalogitem_id).one()

    global USER_ID
    if 'username' in login_session:
        USER_ID = getUserID(login_session['email'])
    return render_template(
                    'viewcatalogitem.html', catalogitem=viewcatalogitem,
                    login_session=login_session, userID=USER_ID)


@app.route(
        '/catalog/<int:catalog_id>/<int:catalogitem_id>/delete',
        methods=['GET', 'POST'])
def deleteCatalogItem(catalog_id, catalogitem_id):
    if 'username' not in login_session:
        redirect_url = "/catalog/"+str(catalog_id)+"/"+str(
                                                    catalogitem_id)+"/delete"
        return redirect('/catalog/login?redirect_url='+redirect_url)

    USER_ID = getUserID(login_session['email'])
    deletecatalogitem = session.query(CatalogItem).filter_by(
                                                    id=catalogitem_id).one()
    if deletecatalogitem.user_id != USER_ID:
        return redirect('catalog/unauthorisederror')

    if request.method == 'POST':
        session.delete(deletecatalogitem)
        flash('%s Successfully Deleted' % deletecatalogitem.name)
        session.commit()
        return redirect(url_for('catalogItemList', catalog_id=catalog_id))
    else:
        return render_template(
                    'deletecatalogitem.html', catalogitem=deletecatalogitem,
                    login_session=login_session)


@app.route('/catalog/JSON')
@app.route('/catalog.JSON')
def catalogJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(Catalog=[r.serialize for r in catalogs])


@app.route('/catalog/<int:catalog_id>/<int:catalogitem_id>/JSON')
def catalogItemJSON(catalog_id, catalogitem_id):
    catalogItems = session.query(CatalogItem).filter_by(
                                                id=catalogitem_id).one()
    return jsonify(CatalogItem=[catalogItems.serialize])


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
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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
    output += '"style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
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
    except Exception:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
                                                                access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        USER_ID = None
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("User is successfully logged out")
        return redirect(url_for('catalogMenu'))

    else:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
                        json.dumps('Failed to revoke token for given user.'),
                        400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/unauthorisederror')
def unauthorisedError():
    return render_template("unauthorisedPage.html")


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
