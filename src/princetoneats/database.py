import sqlalchemy
import sqlalchemy.orm
import dotenv
import os
import sys

dotenv.load_dotenv()
# DATABASE_URL = os.environ["DATABASE_URL"]
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


def _create_database(DATABASE_URL):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        engine.dispose()
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def _remove_user(username):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            row = query.one_or_none()

            in_table = row is not None

            if in_table:
                session.delete(row)

            session.commit()

        engine.dispose()

        return in_table

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


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


def set_user_prefs(username, veg, halal, glutenfree, dairyfree, peanutfree):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            row = query.one_or_none()

            if row is None:
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
                row.veg = veg
                row.halal = halal
                row.glutenfree = glutenfree
                row.dairyfree = dairyfree
                row.peanutfree = peanutfree

            session.commit()

        engine.dispose()

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def get_user_prefs(username):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            row = query.one_or_none()
            if row is None:
                result = None
            else:
                result = {
                    "veg": row.veg,
                    "halal": row.halal,
                    "glutenfree": row.glutenfree,
                    "dairyfree": row.dairyfree,
                    "peanutfree": row.peanutfree,
                }

            session.commit()

        engine.dispose()

        return result
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def add_fav_meal(username, meal_name):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            user = query.one_or_none()
            # if no user in table add empty user
            if user is None:
                user = add_user(username, session)

            if meal_name not in user.fav_meals:
                user.fav_meals += "," + meal_name

            session.commit()

        engine.dispose()

        # return result
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def remove_fav_meal(username, meal_name):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            user = query.one_or_none()
            # if no user in table add empty user
            if user is None:
                ret = False
            else:
                ret = meal_name in user.fav_meals
                if meal_name in user.fav_meals:
                    user.fav_meals = user.fav_meals.replace(meal_name, "")

            session.commit()

        engine.dispose()
        return ret

        # return result
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def is_fav_meal(username, meal_name):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            user = query.one_or_none()
            # if no user in table add empty user
            if user is None:
                user = add_user(username, session)

            is_fav_meal = meal_name in user.fav_meals

            session.commit()

        engine.dispose()

        return is_fav_meal
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


def get_fav_meals(username, meal_name):
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            query = session.query(UserPreference).filter(
                UserPreference.username == username
            )

            user = query.one_or_none()
            # if no user in table add empty user
            fav_meals = "" if user is None else user.fav_meals

            session.commit()

        engine.dispose()

        return fav_meals

        # return result
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


# def db_helper(username, callback_func):
#     """The callback_func takes the user object and db session and
#      will update the db and/or return a value """
#     try:
#         engine = sqlalchemy.create_engine(DATABASE_URL)

#         with sqlalchemy.orm.Session(engine) as session:
#             query = session.query(UserPreference).filter(
#                 UserPreference.username == username
#             )

#             user = query.one_or_none()

#             ret = callback_func(user, session)

#             session.commit()

#         engine.dispose()

#         return ret

#         # return result
#     except Exception as ex:
#         print(ex, file=sys.stderr)
#         sys.exit(1)


if __name__ == "__main__":
    """ Test client """

    # _create_database(DATABASE_URL=DATABASE_URL)

    _remove_user("ya1653")
    _remove_user("ai0492")

    set_user_prefs("ya1653", False, True, False, False, False)
    print(get_user_prefs("ya1653"))
    set_user_prefs("ya1653", True, True, False, False, False)
    print(get_user_prefs("ya1653"))
    # Nonexistent user
    print(get_user_prefs("ya1654"))

    add_fav_meal("ya1653", "A")

    assert is_fav_meal("ya1653", "A")
    assert not is_fav_meal("ya1653", "B")

    # duplicate meal should only be added once
    add_fav_meal("ya1653", "A")
    add_fav_meal("ya1653", "B")

    remove_fav_meal("ya1653", "A")
    assert not is_fav_meal("ya1653", "A")
    assert is_fav_meal("ya1653", "B")

    # user not already in table
    add_fav_meal("ai0492", "A")
    assert is_fav_meal("ai0492", "A")
