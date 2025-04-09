# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

import flask
import dotenv
import os
from scrapedining import get_meal_info
import auth
import re
from collections import defaultdict

import database

# -----------------------------------------------------------------------

app = flask.Flask(__name__)

dotenv.load_dotenv()
app.secret_key = os.environ["APP_SECRET_KEY"]

# -----------------------------------------------------------------------


@app.route("/")
def home():
    # check session for user info
    user_info = flask.session.get("user_info")
    username = None if user_info is None else user_info["user"]

    return flask.render_template("index.html", username=username)


@app.route("/find_meals")
def find_meals():
    vegan_vegetarian = False
    halal = False
    gluten_free = False
    dairy_free = False
    peanut_free = False

    if auth.is_authenticated():
        user_info = auth.authenticate()
        preferences = database.get_user_prefs(user_info["user"])
        if preferences is not None:
            vegan_vegetarian = preferences["veg"]
            halal = preferences["halal"]
            gluten_free = preferences["glutenfree"]
            dairy_free = preferences["dairyfree"]
            peanut_free = preferences["peanutfree"]

    return flask.render_template(
        "find_meals.html",
        vegan_vegetarian=vegan_vegetarian,
        halal=halal,
        gluten_free=gluten_free,
        dairy_free=dairy_free,
        peanut_free=peanut_free,
    )


@app.route("/meals_list", methods=["GET"])
def meals_list():
    diningHall = flask.request.args.get("DHfilter").split(",")
    mealTimes = flask.request.args.get("MTfilter").split(",")
    preferences = flask.request.args.get("ARfilter").split(",")

    if auth.is_authenticated():
        veg = "vegan-vegetarian" in preferences
        halal = "halal" in preferences
        glutenfree = "gluten-free" in preferences
        dairyfree = "dairy-free" in preferences
        peanutfree = "peanut-free" in preferences
        user_info = auth.authenticate()
        database.set_user_prefs(
            user_info["user"], veg, halal, glutenfree, dairyfree, peanutfree
        )

    mealsDict = get_meal_info(diningHall, None, mealTimes[0])

    grouped_meals = defaultdict(list)
    for meal in mealsDict:
        grouped_meals[meal["dhall"]].append(meal)

    return flask.render_template("meals_list.html", grouped_meals=grouped_meals)


# -----------------------------------------------------------------------


@app.route("/logincas", methods=["GET"])
def logincas():
    # Log in to CAS and redirect home
    user_info = auth.authenticate()
    username = user_info["user"]
    print(username)
    return flask.redirect(flask.url_for("home"))


@app.route("/logoutcas", methods=["GET"])
def logoutcas():
    # Log out of the CAS session then redirect home
    logout_url = (
        auth._CAS_URL
        + "logout?service="
        + auth.urllib.parse.quote(re.sub("logoutcas", "logoutapp", flask.request.url))
    )
    flask.abort(flask.redirect(logout_url))


@app.route("/logoutapp", methods=["GET"])
def logoutapp():
    # Log out of the application and redirect home
    flask.session.clear()
    return flask.redirect(flask.url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
