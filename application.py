from flask import Flask, render_template, request, redirect, url_for, abort, flash, jsonify
from sqlalchemy import asc, exists
from database_setup import User, Category, Item, session
from flask import session as login_session
from werkzeug.routing import BuildError
from os import urandom
from base64 import b64encode
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import hashlib

import config
import pycurl
import urllib
import json
from io import BytesIO

app = Flask(__name__)
app.secret_key = "\xc7\xc7\xf7\x80\x9b\xbb'\xd7\xa7\xe4\xa8\xd9\x7f\x03z)u&Z2c\xde\xf0\xd8"
app.config['SESSION_TYPE'] = 'filesystem'

# API Rate Limit configuration
limiter = Limiter(
    app,
    key_func=get_remote_address
)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    # response = jsonify(error.to_dict())
    # response.status_code = error.status_code
    # return response
    flash(error.message, 'error')
    return redirect(url_for('show_homepage'))


@app.before_request
def csrf_protect():
    """
    Intercept POST requests and check the token
    (if it's not an API request)
    See http://flask.pocoo.org/snippets/3/
    :return:
    """
    if request.method == "POST" and request.path[0:5] != "/api/":
        token = login_session.pop('_csrf_token', None)
        request_token = request.form.get('_csrf_token')
        print("Comparing server token [" + token + "]")
        print("with client token [" + request_token + "]")
        if not token or token != request_token:
            print("Tokens do not match! Aborting..")
            abort(403)
        print("Tokens match - accepted")


@app.before_request
def ensure_user_in_database():
    """
    If app has been restarted and user still has a session
    it might be necessary to recreate the user in the
    database (especially if using in-memory database)
    """
    if 'email' in login_session:
        user_exists = session.query(exists().where(User.email == login_session['email'])).scalar()
        if not user_exists:
            user = User(
                id=login_session['userid'],
                picture=login_session['picture'],
                name=login_session['name'],
                email=login_session['email'],
                client_id=login_session['client_id']
            )
            session.add(user)
            session.commit()
            print("Recreated user in database")


def generate_csrf_token():
    """
    Generate CSRF token on new pages
    :return: The token
    """
    if '_csrf_token' not in login_session:
        login_session['_csrf_token'] = b64encode(urandom(64)).decode()  # Cryptographically secure random key
    print ("_csrf_token:" + login_session['_csrf_token'])
    return login_session['_csrf_token']


def request_wants_json():
    """
    Helper function to check if incoming requests are for HTML or JSON
    and then either render a page or return the jsonified results
    :return: true if JSON wanted instead of HTML
    """
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


@app.route('/')
def show_homepage():
    """
    Shows all the available categories and items
    """
    max_items = 5
    all_categories = session.execute(
        'SELECT category.name, category.id, count(item.id) AS item_count '
        'FROM category '
        'LEFT JOIN item ON category.id = item.category_id '
        'GROUP BY category.name, category.id')
    items = session.query(Item, Category).join(Category).order_by(Item.time_updated.desc(), Item.time_created.desc(),
                                                                  Item.name).limit(5).all()
    return render_template('categories_latest.html',
                           all_categories=all_categories,
                           items=items,
                           max_items=max_items,
                           login_session=login_session)


@app.route('/logout')
def logout_redirect():
    """
    Redirect to home page and confirm logout to user
    """
    login_session.clear()
    flash('You have logged out')
    return redirect(url_for('show_homepage'))


@app.route('/profile')
def show_profile():
    """
    Show user profile including the APP_ID which is required for modifications using JSON
    """
    print ('LOGIN SESSION:', login_session)
    if 'userid' in login_session:
        category = session.query(Category).first()
        item = session.query(Item).first()
        return render_template('profile.html', login_session=login_session, root=app.instance_path, category=category,
                               item=item)
    flash('Unfortunately you need to be logged in to see your profile', 'error')
    return redirect(url_for('show_homepage'))


@app.route('/categories/<int:category_id>/items')
def show_category_items(category_id):
    """
    Displays all the items for the specified category
    """
    all_categories = session.execute(
        'SELECT category.name, category.id, count(item.id) AS item_count '
        'FROM category LEFT JOIN item ON category.id = item.category_id '
        'GROUP BY category.name, category.id')
    category = session.query(Category).filter(Category.id == category_id).first()
    items = session.query(Item).filter(Item.category_id == category_id)
    item_count = items.count()
    return render_template('category_items.html',
                           all_categories=all_categories,
                           category=category,
                           items=items,
                           item_count=item_count,
                           login_session=login_session)


@app.route('/api/categories')
@limiter.limit("100/hour")
@limiter.limit("2/minute")
def api_categories():
    """
    Rate-limited JSON API to retrieve all categories
    """
    categories = session.query(Category)
    return jsonify(json_list=[i.to_json() for i in categories.all()])


@app.route('/api/categories/<int:category_id>/items')
@limiter.limit("100/hour")
@limiter.limit("2/minute")
def api_category_items(category_id):
    """
    Rate-limited JSON API to retrieve items for a specified category
    """
    items = session.query(Item).filter(Item.category_id == category_id)
    return jsonify(json_list=[i.to_json() for i in items.all()])


@app.route('/api/items/<int:item_id>', methods=['GET', 'POST'])
@limiter.limit("100/hour")
@limiter.limit("2/minute")
def api_item_details(item_id):
    """
    Displays or edits specified item
    """
    if request.method == 'GET':
        item = session.query(Item, User).join(User).filter(Item.id == item_id).first()
        return jsonify(item.Item.to_json())
        # TODO - Add a POST method + HTTP Auth to allow a RESTful item modification


@app.route('/items/<int:item_id>')
def show_item_details(item_id):
    """
    Displays full description of an item
    """
    item = session.query(Item, User).join(User).filter(Item.id == item_id).first()
    return render_template('item_details.html', item=item, login_session=login_session)


def is_user_the_creator(item_id):
    """
    Return Item for specified ID if logged in
    user is also the creator of the target item
    Otherwise, redirect to safe home page with user message
    :param item_id:
    :return: The item + user record
    """
    # User must be logged in for GET and POST
    if 'userid' not in login_session:
        # flash('Unfortunately you need to be logged in to make changes', 'error')
        # return redirect(url_for('show_homepage'))
        raise InvalidUsage('Unfortunately you need to be logged in to make changes', status_code=403)

    item = session.query(Item, User).outerjoin(User).filter(Item.id == item_id).first()

    # For existing items, user must be item creator
    if item and item.Item.user_id != login_session['userid']:
        # flash('Unfortunately this item was not created by you', 'error')
        # return redirect(url_for('show_homepage'))
        raise InvalidUsage('Unfortunately this item was not created by you', status_code=403)
    return item


@app.route('/items/<int:item_id>/delete', methods=['POST', 'GET'])
def delete_item_details(item_id):
    """
    Delete item for specified ID
    CSRF Token regenerated for each new page
    :param item_id:
    :return:
    """
    item = is_user_the_creator(item_id)
    item_name = item.Item.name
    if request.method == 'GET':
        return render_template('item_delete_confirm.html', item_name=item_name, item_id=item_id,
                               login_session=login_session,
                               csrf_token=generate_csrf_token())
    else:
        session.delete(item.Item)
        session.commit()
        flash(item_name + " deleted")
        return redirect(url_for('show_homepage'))


@app.route('/items/<int:item_id>/edit', methods=['POST', 'GET'])
def edit_item_details(item_id):
    """
    Modify specified item
    item_id >= 1  =>  UPDATE item  (if user is original creator)
    item_id == 0  =>  CREATE item
    """
    category_id = None
    if 'category_id' in request.args:
        category_id = int(request.args['category_id'])
    if 'userid' not in login_session:
        flash('Unfortunately you need to be logged in to make changes', 'error')
        return redirect(url_for('show_homepage'))

    item = None
    if item_id != 0:
        item = is_user_the_creator(item_id)
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.name)).all()
        return display_item(categories, item, item_id, category_id)
    else:
        return save_item(item, item_id)


def save_item(item, item_id):
    """
    Utility method for updating an existing
    item or creating a new item
    :param item:
    :param item_id:
    :return: Rendered html
    """
    # User is modifying an EXISTING item in the database
    if item_id > 0:
        item.Item.name = request.form['title']
        item.Item.description = request.form['description']
        item.Item.category_id = request.form['category']
        session.add(item.Item)
        session.commit()
        flash("Updated " + item.Item.name)
        return render_template('item_details.html', item=item, login_session=login_session)

    # User is creating a NEW item
    else:
        new_item = Item(name=request.form.get('title'), description=request.form['description'],
                        category_id=request.form['category'],
                        user_id=login_session['userid'])
        session.add(new_item)
        session.commit()
        flash("Created " + new_item.name)
        created_item = session.query(Item, User).filter(Item.id == new_item.id).join(User).first()
        return render_template('item_details.html', item=created_item, login_session=login_session)


def display_item(categories, item, item_id, initial_category_id):
    """
    Utility class for rendering a page for edit of existing item or creation of new item.
    CSRF Token regenerated for each new page
    """
    if item:
        # Item already exists - display on page
        return render_template('item_edit.html', item_id=item_id, item_name=item.Item.name,
                               item_description=item.Item.description, item_category=item.Item.category,
                               item_category_id=item.Item.category_id, categories=categories,
                               login_session=login_session,
                               csrf_token=generate_csrf_token())
    else:
        print ('initial_category_id', initial_category_id)
        # Default fields for creating a new item
        return render_template('item_edit.html', item_id=0, item_name="",
                               item_description="", item_category="",
                               item_category_id=initial_category_id, categories=categories,
                               login_session=login_session, initial_category_id=initial_category_id,
                               csrf_token=generate_csrf_token())


def redirect_dest(fallback):
    destination = request.args.get('next')
    try:
        destination_url = url_for(destination)
    except BuildError:
        return redirect(fallback)
    return redirect(destination_url)


@app.route('/login')
def login_redirect():
    """
    Redirect from Amazon Login with an auth token
    :return:
    """
    next_redirect = request.args.get('next')
    access_token = request.args.get('access_token')
    d = amazon_authorization(access_token)
    print ("Amazon data:", d)
    # # State token to prevent CSRF
    # state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    # login_session['state'] = state
    # Find user in database by email or create new record
    user = session.query(User).filter(User.email == d['email']).first()
    if user is None:
        print ("Creating new user in database")
        m = hashlib.md5()
        m.update(d['email'])
        gravatar = 'https://secure.gravatar.com/avatar/' + m.hexdigest() + '?size=35'
        user = User(name=d['name'], email=d['email'], picture=gravatar)
        session.add(user)
        session.commit()

    # Update the Amazon ID for the user if not already set
    if user.client_id != d['user_id']:
        user.client_id = d['user_id']
        session.commit()

    login_session['userid'] = user.id
    login_session['picture'] = user.picture
    login_session['name'] = user.name
    login_session['email'] = user.email
    login_session['client_id'] = user.client_id

    flash('You were successfully logged in')

    return redirect_dest(next_redirect)


def amazon_authorization(access_token):
    """
    Encapsulates the SDK code from Amazon
    :param access_token: Access token provided by Amazon callback
    :return: Object containing user credentials if authenticated
    """
    b = BytesIO()
    # verify that the access token belongs to us
    c = pycurl.Curl()
    c.setopt(pycurl.URL, "https://api.amazon.com/auth/o2/tokeninfo?access_token=" + urllib.quote_plus(access_token))
    c.setopt(pycurl.SSL_VERIFYPEER, 1)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()
    d = json.loads(b.getvalue())
    if d['aud'] != config.YOUR_CLIENT_ID:
        # the access token does not belong to us
        raise BaseException("Invalid Token")

    # exchange the access token for user profile
    b = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, "https://api.amazon.com/user/profile")
    c.setopt(pycurl.HTTPHEADER, ["Authorization: bearer " + access_token])
    c.setopt(pycurl.SSL_VERIFYPEER, 1)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()
    d = json.loads(b.getvalue())
    return d
