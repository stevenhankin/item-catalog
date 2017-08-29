import database_setup
import database_populate
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, asc, desc, text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session

import hashlib

import config
import pycurl
import urllib
import json
import StringIO

app = Flask(__name__)

engine = create_engine('sqlite:///itemcategories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Show all Categories and latest Items
@app.route('/')
def show_homepage():
    max_items = 5
    all_categories = session.query(Category).order_by(asc(Category.name)).all()
    # if 'username' not in login_session:
    #     return render_template('public_categories.html', categories=categories)
    # else:
    s = "select item.name as item_name, category.name as category_name, " \
        " category.id as category_id " \
        " from item" \
        " join category on (item.category_id = category.id)" \
        " order by item.time_created DESC" \
        " limit " + str(max_items)
    latest_items = session.execute(s).fetchall()
    return render_template('categories_latest.html',
                           all_categories=all_categories,
                           latest_items=latest_items,
                           max_items=max_items)


# For specified category, display all items
@app.route('/category/<int:category_id>/items')
def show_category_items(category_id):
    print "category_id " + str(category_id)
    all_categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter(Category.id == category_id).first()
    items = session.query(Item).filter(Item.category_id == category_id)
    item_count = items.count()
    return render_template('category_items.html',
                           all_categories=all_categories,
                           category=category,
                           items=items,
                           item_count=item_count)


# Displays item description
@app.route('/category/<int:category_id>/items/<int:item_id>')
def show_item_details(category_id, item_id):
    print "item_id " + str(item_id)
    # all_categories = session.query(Category).order_by(asc(Category.name)).all()
    # category = session.query(Category).filter(Category.id == category_id).first()
    item = session.query(Item).filter(Item.id == item_id).one()
    # item_count = items.count()
    print item.description
    return render_template('item_details.html', item=item)


def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)


# Redirect (from Amazon)
@app.route('/login')
def login_redirect():
    access_token = request.args.get('access_token')
    print "access token is " + access_token

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

    print "%s %s %s" % (d['name'], d['email'], d['user_id'])

    user = session.query(User).filter(User.email == d['email']).first()
    print user
    if user is None:
        m = hashlib.md5()
        m.update(d['email'])
        gravatar = 'https://secure.gravatar.com/avatar/' + m.hexdigest() + '?size=35'
        user = User(name=d['name'], email=d['email'], picture=gravatar)
        session.add(user)
        session.commit()

    return redirect_dest('/')
