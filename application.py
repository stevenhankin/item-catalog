from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session

app = Flask(__name__)


engine = create_engine('sqlite:///itemcategories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all Categories
@app.route('/')
@app.route('/category/')
def show_categories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    # if 'username' not in login_session:
    #     return render_template('public_categories.html', categories=categories)
    # else:
    latest_items = session.query(Item).order_by(desc(Item.time_created)).limit(5)
    return render_template('categories.html', categories=categories, latest_items=latest_items)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
