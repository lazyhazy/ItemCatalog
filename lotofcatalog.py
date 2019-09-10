from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from database_setup import Catalog, Base, CatalogItem, User

engine = create_engine('sqlite:///catalogmenu.db')
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
User1 = User(name="Karthik Narayanan", email="checkitoutkarthik@gmail.com")
session.add(User1)
session.commit()

# Adding a Catalog "Soccer"
catalog1 = Catalog(name="Soccer")
session.add(catalog1)
session.commit()

# Adding a Catalog Item under Soccer Catalog
catalogitem1 = CatalogItem(
            name="Shinguards",
            description="This is Shinguards item belongs to Soccer Catalog",
            datecreated=datetime.datetime.now(),
            catalog=catalog1,
            user_id=1)
session.add(catalogitem1)
session.commit()

# Adding a Catalog Item under Soccer Catalog
catalogitem2 = CatalogItem(
                name="Jersey",
                description="This is Jersey item belongs to Soccer Catalog",
                datecreated=datetime.datetime.now(),
                catalog=catalog1,
                user_id=1)
session.add(catalogitem2)
session.commit()

# Adding a Catalog Item under Soccer Catalog
catalogitem3 = CatalogItem(
            name="Soccer Cleats",
            description="This is Soccer Cleats item belongs to Soccer Catalog",
            datecreated=datetime.datetime.now(),
            catalog=catalog1,
            user_id=1)
session.add(catalogitem3)
session.commit()


# Adding Catalog Item "BasketBall"
catalog2 = Catalog(name="BasketBall")
session.add(catalog2)
session.commit()

# Adding Catalog Item under BasketBall Category
catalogitem1 = CatalogItem(
                name="Ball",
                description="This is Ball item belongs to Basketball Category",
                datecreated=datetime.datetime.now(),
                catalog=catalog2,
                user_id=1)
session.add(catalogitem1)
session.commit()


# Adding Catalog Item "Baseball"
catalog3 = Catalog(name="Baseball")
session.add(catalog3)
session.commit()

# Adding Catalog Item under Baseball Category
catalogitem1 = CatalogItem(
                name="Bat",
                description="This is Bat item belongs to Baseball Category",
                catalog=catalog3,
                user_id=1)
session.add(catalogitem1)
session.commit()


# Adding Catalog Item "Frisbee"
catalog4 = Catalog(name="Frisbee")
session.add(catalog4)
session.commit()

# Adding Catalog Item under Frisbee Category
catalogitem1 = CatalogItem(
                name="Frisbee",
                description="This is Frisbee item belongs to Frisbee Category",
                catalog=catalog4,
                user_id=1)
session.add(catalogitem1)
session.commit()


# Adding Catalog Item "Snowboarding"
catalog5 = Catalog(name="Snowboarding")
session.add(catalog5)
session.commit()

# Adding Catalog Item under Snowboarding Category
catalogitem1 = CatalogItem(
            name="Goggles",
            description="This is Goggles belongs to Snowboarding Category",
            catalog=catalog5,
            user_id=1)
session.add(catalogitem1)
session.commit()

# Adding Catalog Item under Snowboarding Category
catalogitem2 = CatalogItem(
            name="Snowboard",
            description="This is Snowboard belongs to Snowboarding Category",
            catalog=catalog5,
            user_id=1)
session.add(catalogitem1)
session.commit()


# Adding Catalog Item "Rock Climbing"
catalog6 = Catalog(name="Rock Climbing")
session.add(catalog6)
session.commit()


# Adding Catalog Item "Foosball"
catalog7 = Catalog(name="Foosball")
session.add(catalog7)
session.commit()


# Adding a Catalog - "Skating"
catalog8 = Catalog(name="Skating")
session.add(catalog8)
session.commit()


# Adding a Catalog - "Hockey"
catalog9 = Catalog(name="Hockey")
session.add(catalog9)
session.commit()

# Adding a Catalog Item under Hockey Category
catalogitem1 = CatalogItem(
                name="Stick",
                description="This is Stick item belongs to Hockey Category",
                catalog=catalog9,
                user_id=1)
session.add(catalogitem1)
session.commit()


print "added catalog items!"
