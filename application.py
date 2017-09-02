from flask import Flask, render_template, request, redirect, url_for, g, abort, flash
from sqlalchemy import asc, desc, text
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Category, Item, session
from flask import session as login_session


import hashlib

import config
import pycurl
import urllib
import json
import StringIO

import random, string

app = Flask(__name__)
app.secret_key = "\xc7\xc7\xf7\x80\x9b\xbb'\xd7\xa7\xe4\xa8\xd9\x7f\x03z)u&Z2c\xde\xf0\xd8"
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/')
def show_homepage():
    """
    Shows all the available categories and items
    :return:
    """
    max_items = 5
    all_categories = session.query(Category).order_by(asc(Category.name)).all()
    s = "select item.name as item_name, category.name as category_name, " \
        " category.id as category_id " \
        " from item" \
        " join category on (item.category_id = category.id)" \
        " order by ifnull(item.time_updated, item.time_created) DESC" \
        " limit " + str(max_items)
    latest_items = session.execute(s).fetchall()
    return render_template('categories_latest.html',
                           all_categories=all_categories,
                           latest_items=latest_items,
                           max_items=max_items,
                           login_session=login_session)


# For specified category, display all items
@app.route('/categories/<int:category_id>/items')
def show_category_items(category_id):
    """
    Displays all the items for the selected category
    :param category_id:
    :return:
    """
    all_categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter(Category.id == category_id).first()
    items = session.query(Item).filter(Item.category_id == category_id)
    item_count = items.count()
    return render_template('category_items.html',
                           all_categories=all_categories,
                           category=category,
                           items=items,
                           item_count=item_count,
                           login_session=login_session)


@app.route('/categories/<int:category_id>/items/<int:item_id>')
def show_item_details(category_id, item_id):
    """
    Displays full description of an item
    """
    item = session.query(Item, User).join(User).filter(Item.id == item_id).one()
    return render_template('item_details.html', item=item, login_session=login_session)


@app.route('/items/<int:item_id>/delete', methods=['POST', 'GET'])
def delete_item_details(item_id):
    item = asset_user_is_creator(item_id)
    item_name = item.Item.name
    if request.method == 'GET':
        return render_template('item_delete_confirm.html', item_name=item_name, item_id=item_id,
                               login_session=login_session)
    else:
        session.delete(item.Item)
        session.commit()
        flash(item_name + " deleted")
        return redirect(url_for('show_homepage'))


def asset_user_is_creator(item_id):
    """
    Utility to verify that the logged in user
    is also the creator of the target item
    :param item_id:
    :return: The item + user record
    """
    # User must be logged in for GET and POST
    if not login_session.has_key('userid'):
        abort(403, 'Unfortunately you need to be logged in to make changes')
    item = session.query(Item, User).join(User).filter(Item.id == item_id).first()
    # For existing items, user must be item creator
    if item and item.Item.user_id != login_session['userid']:
        abort(403, 'Unfortunately this item was not created by you')
    return item


@app.route('/items/<int:item_id>/edit', methods=['POST', 'GET'])
def edit_item_details(item_id):
    """
    item_id >= 1  =>  UPDATE item  (if user is original creator)
    item_id == 0  =>  CREATE item
    """
    item = asset_user_is_creator(item_id)
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.name)).all()
        return display_item(categories, item, item_id)
    else:
        return save_item(item, item_id)


def save_item(item, item_id):
    """
    For updating an existing item
    or creating a new item
    :param item:
    :param item_id:
    :return:
    """
    # User is modifying an EXISTING item in the database
    if item_id > 0:
        item.Item.name = request.form['title']
        item.Item.description = request.form['description']
        item.Item.category_id = request.form['category']
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
        item = session.query(Item, User).join(User).filter(Item.id == new_item.id).first()
        return render_template('item_details.html', item=item, login_session=login_session)


def display_item(categories, item, item_id):
    if item:
        # Item already exists - display on page
        return render_template('item_edit.html', item_id=item_id, item_name=item.Item.name,
                               item_description=item.Item.description, item_category=item.Item.category,
                               item_category_id=item.Item.category_id, categories=categories,
                               login_session=login_session)
    else:
        # Default fields for creating a new item
        return render_template('item_edit.html', item_id=0, item_name="",
                               item_description="", item_category="",
                               item_category_id=0, categories=categories,
                               login_session=login_session)


def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)


@app.route('/logout')
def logout():
    login_session.clear()
    next_redirect = request.args.get('next')
    flash('You have been logged out')
    return redirect(next_redirect)


@app.route('/login')
def login_redirect():
    """
    Redirect from Amazon Login with an auth token
    :return:
    """
    nextRedirect = request.args.get('next')
    access_token = request.args.get('access_token')
    d = amazon_authorization(access_token)
    # # State token to prevent CSRF
    # state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    # login_session['state'] = state
    # Find user in database by email or create new record
    user = session.query(User).filter(User.email == d['email']).first()
    if user is None:
        m = hashlib.md5()
        m.update(d['email'])
        gravatar = 'https://secure.gravatar.com/avatar/' + m.hexdigest() + '?size=35'
        user = User(name=d['name'], email=d['email'], picture=gravatar)
        session.add(user)
        session.commit()

    login_session['userid'] = user.id
    login_session['picture'] = user.picture
    login_session['name'] = user.name

    flash('You were successfully logged in')

    return redirect_dest(nextRedirect)


def amazon_authorization(access_token):
    """
    Encapsulates the SDK code from Amazon
    :param access_token: Access token provided by Amazon callback
    :return: Object containing user credentials if authenticated
    """
    b = StringIO.StringIO()
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
    b = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, "https://api.amazon.com/user/profile")
    c.setopt(pycurl.HTTPHEADER, ["Authorization: bearer " + access_token])
    c.setopt(pycurl.SSL_VERIFYPEER, 1)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()
    d = json.loads(b.getvalue())
    return d
