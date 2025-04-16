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
    veg = sqlalchemy.Column(sqlalchemy.Boolean)
    halal = sqlalchemy.Column(sqlalchemy.Boolean)
    glutenfree = sqlalchemy.Column(sqlalchemy.Boolean)
    dairyfree = sqlalchemy.Column(sqlalchemy.Boolean)
    peanutfree = sqlalchemy.Column(sqlalchemy.Boolean)


engine = sqlalchemy.create_engine(DATABASE_URL)

# def create_database(DATABASE_URL):
#     try:
#         engine = sqlalchemy.create_engine(DATABASE_URL)

#         Base.metadata.drop_all(engine)
#         Base.metadata.create_all(engine)

#         engine.dispose()
#     except Exception as ex:
#         print(ex, file=sys.stderr)
#         sys.exit(1)


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


if __name__ == "__main__":
    # create_database(DATABASE_URL=DATABASE_URL)
    # set_user_prefs("ya1653", False, True, False, False, False)
    # print(get_user_prefs("ya1653"))
    # set_user_prefs("ya1653", True, True, False, False, False)
    # print(get_user_prefs("ya1653"))
    # print(get_user_prefs("ya1653"))
    pass
