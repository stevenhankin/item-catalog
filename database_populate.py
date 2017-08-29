"""Populates database with initial data."""
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcategories.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


def add_car_items(category, user_id):
    car_item1 = Item(user_id=user_id, category_id=category.id,
                     name="Tesla Model S",
                     description="Full-sized all-electric five-door, luxury "
                                 "liftback, produced by Tesla, Inc., and"
                                 " introduced on 22 June 2012.")
    car_item2 = Item(user_id=user_id, category_id=category.id,
                     name="Aston Martin Vanquish",
                     description="British grand tourer that was introduced in "
                                 "2001 as a successor to the ageing Virage"
                                 " range.")
    car_item3 = Item(user_id=user_id, category_id=category.id,
                     name="Lamborghini Centenario",
                     description="To commemorate Ferruccio Lamborghini's 100th "
                                 "birthday, Lamborghini released a "
                                 "limited-edition supercar based on the "
                                 "Aventador at the March 2016 Geneva Motor "
                                 "Show.")
    session.add_all([car_item1, car_item2, car_item3])


def add_food_items(category, user_id):
    food_item1 = Item(user_id=user_id, category_id=category.id,
                      name="Cottage Pie",
                      description="Beef pie with a topping of mashed potato, "
                                  "not pastry.")
    food_item2 = Item(user_id=user_id, category_id=category.id,
                      name="Chicken Tikka Masala",
                      description="Dish of chunks of roasted marinated chicken"
                                  " (chicken tikka) in a spiced curry sauce. "
                                  "The sauce is usually creamy and "
                                  "orange-coloured.")
    session.add_all([food_item1, food_item2])


def add_cat_items(category, user_id):
    cat_item1 = Item(user_id=user_id, category_id=category.id,
                     name="British Shorthair",
                     description="The British Shorthair is the pedigreed "
                                 "version of the traditional British domestic "
                                 "cat, with a distinctively chunky body, dense"
                                 " coat and broad face.")
    cat_item2 = Item(user_id=user_id, category_id=category.id,
                     name="Chartreux",
                     description="The Chartreux is a rare breed of domestic cat"
                                 " from France and is recognised by a number of"
                                 " registries around the world.")
    session.add_all([cat_item1, cat_item2])


def add_categories(user_id):
    """Categories for Cars, Food and Cats. A short delay is used between
    adding items to categories to ensure that there is a "latest" ordering
    :param user_id: ID of user that has created these categories and items
    :return:
    """
    category1 = Category(user_id=user_id, name="Cars")
    category2 = Category(user_id=user_id, name="Food")
    category3 = Category(user_id=user_id, name="Cats")
    session.add_all([category1, category2, category3])
    session.commit()
    # Add items to respective categories using sleep and
    # commit to generate delay for time created values
    add_car_items(category1, user_id)
    time.sleep(1)
    session.commit()
    add_food_items(category2, user_id)
    time.sleep(1)
    session.commit()
    add_cat_items(category3, user_id)
    session.commit()


def populate_if_empty():
    category_count = session.query(Category).count()
    print "Table Category has " + str(category_count) + " records"
    if category_count == 0:
        print "Database appears empty. Adding some records..."
        # Create user and associated records
        User1 = User(name="Steven Hankin",
                     email="steven.hankin@hmail.com",
                     picture="https://secure.gravatar.com/avatar/bbed4d2a6f627e45d8de9ed6e0c0a468?size=35")
        session.add(User1)
        session.commit()
        print "Creating categories..."
        add_categories(User1.id)
    else:
        print "Database already contains data (no new records created)"


populate_if_empty()
