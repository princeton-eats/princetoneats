import sqlalchemy
import sqlalchemy.orm
import dotenv
import os
import sys

dotenv.load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///default.db")
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


class UserPreference(Base):
    __tablename__ = "userprefs"
    username = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    fav_meals = sqlalchemy.Column(sqlalchemy.String)
    veg = sqlalchemy.Column(sqlalchemy.Boolean)
    halal = sqlalchemy.Column(sqlalchemy.Boolean)
    glutenfree = sqlalchemy.Column(sqlalchemy.Boolean)
    dairyfree = sqlalchemy.Column(sqlalchemy.Boolean)
    peanutfree = sqlalchemy.Column(sqlalchemy.Boolean)


engine = sqlalchemy.create_engine(DATABASE_URL)

# ------------------------------------------------------------


# Database manegement
def _create_database():
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        engine.dispose()
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def _db_helper(username, callback_func):
    """The callback_func takes the user object and db session and
    will update the db and/or return a value"""
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            user = query.one_or_none()

            ret = callback_func(user, session)

            session.commit()

        engine.dispose()

        return ret

        # return result
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


# ------------------------------------------------------------


#  Functions for maneging users
def _remove_user(username):
    def callback_func(user, session):
        in_table = user is not None

        if in_table:
            session.delete(user)

    _db_helper(username, callback_func)


def add_user(username, session):
    user = UserPreference(
        username=username,
        fav_meals="",
        veg=False,
        halal=False,
        glutenfree=False,
        dairyfree=False,
        peanutfree=False,
    )
    session.add(user)
    session.commit()
    return user


# ------------------------------------------------------------


# Setters and getters for  user preferences
def set_user_prefs(username, veg, halal, glutenfree, dairyfree, peanutfree):
    def callback_func(user, session):
        if user is None:
            user = UserPreference(
                username=username,
                fav_meals="",
                veg=veg,
                halal=halal,
                glutenfree=glutenfree,
                dairyfree=dairyfree,
                peanutfree=peanutfree,
            )
            session.add(user)
        else:
            user.veg = veg
            user.halal = halal
            user.glutenfree = glutenfree
            user.dairyfree = dairyfree
            user.peanutfree = peanutfree

        return {
            "fav_meals": user.fav_meals,
            "preferences": {
                "vegan-vegetarian": user.veg,
                "halal": user.halal,
                "gluten-free": user.glutenfree,
                "dairy-free": user.dairyfree,
                "peanut-free": user.peanutfree,
            },
        }

    return _db_helper(username, callback_func)


def get_user_info(username):
    def callback_func(user, session):
        if user is None:
            return {
                "fav_meals": "",
                "preferences": {
                    "vegan-vegetarian": False,
                    "halal": False,
                    "gluten-free": False,
                    "dairy-free": False,
                    "peanut-free": False,
                },
            }
        else:
            return {
                "fav_meals": user.fav_meals,
                "preferences": {
                    "vegan-vegetarian": user.veg,
                    "halal": user.halal,
                    "gluten-free": user.glutenfree,
                    "dairy-free": user.dairyfree,
                    "peanut-free": user.peanutfree,
                },
            }

    return _db_helper(username, callback_func)


# ------------------------------------------------------------


# Favorite meal functionality
def add_fav_meal(username, meal_name):
    def callback_func(user, session):
        if user is None:
            user = add_user(username, session)

        if meal_name not in user.fav_meals:
            user.fav_meals += "," + meal_name
        return user is None

    return _db_helper(username, callback_func)


def remove_fav_meal(username, meal_name):
    def callback_func(user, session):
        if user is None:
            ret = False
        else:
            ret = meal_name in user.fav_meals
            if meal_name in user.fav_meals:
                user.fav_meals = user.fav_meals.replace(meal_name, "")
        return ret

    return _db_helper(username, callback_func)


def is_fav_meal(username, meal_name):
    def callback_func(user, session):
        if user is None:
            return False
        return meal_name in user.fav_meals

    return _db_helper(username, callback_func)


# ------------------------------------------------------------

# Testing
if __name__ == "__main__":
    """ Test client """

    # _create_database(DATABASE_URL=DATABASE_URL)

    # _remove_user("ya1653")
    # _remove_user("ai0492")

    # set_user_prefs("ya1653", False, True, False, False, False)
    # print(get_user_prefs("ya1653"))
    # set_user_prefs("ya1653", True, True, False, False, False)
    # print(get_user_prefs("ya1653"))
    # # Nonexistent user
    # print(get_user_prefs("ya1654"))

    # add_fav_meal("ya1653", "A")

    # assert is_fav_meal("ya1653", "A")
    # assert not is_fav_meal("ya1653", "B")

    # # duplicate meal should only be added once
    # add_fav_meal("ya1653", "A")
    # add_fav_meal("ya1653", "B")

    # remove_fav_meal("ya1653", "A")
    # assert not is_fav_meal("ya1653", "A")
    # assert is_fav_meal("ya1653", "B")

    # # user not already in table
    # add_fav_meal("ai0492", "A")
    # assert is_fav_meal("ai0492", "A")
