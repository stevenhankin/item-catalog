from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, asc, desc, text
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
def show_category_items():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    # if 'username' not in login_session:
    #     return render_template('public_categories.html', categories=categories)
    # else:
    s = "select item.name as item_name, category.name as category_name" \
        " from item" \
        " join category on (item.category_id = category.id)" \
        " order by item.time_created DESC" \
        " limit 5"
    latest_items = session.execute(s).fetchall()
    return render_template('categories.html', categories=categories, latest_items=latest_items)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
