"""Populates database with initial data."""
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


# Create dummy user
User1 = User(name="Steven Hankin",
             email="steven.hankin@hmail.com",
             picture="https://pbs.twimg.com/profile_images/2671170543"
             + "/18debd694829ed78203a5a36dd364160_400x400.png")
session.add(User1)
session.commit()

# Category for Cars
category1 = Category(user_id=User1.id, name="Cars")
session.add(category1)
# Category for Food
category2 = Category(user_id=User1.id, name="Food")
session.add(category2)
# Category for Cats
category3 = Category(user_id=User1.id, name="Cats")
session.add(category3)
session.commit()

# Items for Car category
session.add(
    Item(user_id=User1.id, category_id=category1.id,
         name="Tesla Model S",
         description="Full-sized all-electric five-door, luxury "
         + "liftback, produced by Tesla, Inc., and introduced "
         + "on 22 June 2012."))
session.add(
    Item(user_id=User1.id, category_id=category1.id,
         name="Aston Martin Vanquish",
         description="British grand tourer that was introduced in 2001 as"
         + " a successor to the ageing Virage range."))
session.add(
    Item(user_id=User1.id, category_id=category1.id,
         name="Lamborghini Centenario",
         description="British grand tourer that was introduced in 2001 as"
         + " a successor to the ageing Virage range."))
session.commit()

# Items for Food category
session.add(
    Item(user_id=User1.id, category_id=category2.id,
         name="Cottage Pie",
         description="Beef pie with a topping of mashed potato, not pastry."))
session.add(
    Item(user_id=User1.id, category_id=category2.id,
         name="Chicken Tikka Masala",
         description="dish of chunks of roasted marinated chicken (chicken tikka) in a spiced curry sauce. The sauce is usually creamy and orange-coloured."))
session.commit()

# Items for Cat category
session.add(
    Item(user_id=User1.id, category_id=category3.id,
         name="British Shorthair",
         description="The British Shorthair is the pedigreed version of the traditional British domestic cat, with a distinctively chunky body, dense coat and broad face."));
session.add(
    Item(user_id=User1.id, category_id=category3.id,
         name="Chartreux",
         description="The Chartreux is a rare breed of domestic cat from France and is recognised by a number of registries around the world."))
session.commit()
