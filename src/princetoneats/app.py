# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

import random
import flask
import dotenv
import os
import scrapedining
import auth
import re
import datetime
from collections import defaultdict
import asyncio

import database

# -----------------------------------------------------------------------

app = flask.Flask(__name__)

dotenv.load_dotenv()
app.secret_key = os.environ.get("APP_SECRET_KEY", "dev_secret_key_for_testing")

# -----------------------------------------------------------------------


# Home Page
@app.route("/")
def home():
    # check session for user info
    user_info = flask.session.get("user_info")
    username = None if user_info is None else user_info["user"]

    if username is not None:
        return flask.redirect(flask.url_for("dashboard"))

    return flask.render_template("index.html", username=username)


# -----------------------------------------------------------------------


# About Page
@app.route("/about")
def about():
    # check session for user info
    user_info = flask.session.get("user_info")
    username = None if user_info is None else user_info["user"]

    return flask.render_template("about.html", username=username)


# -----------------------------------------------------------------------


# Dashboard Page
@app.route("/dashboard")
def dashboard():
    # check session for user info
    user_info = flask.session.get("user_info")
    if user_info is None:
        return flask.redirect(flask.url_for("home"))

    username = user_info["user"]
    userFirstname = user_info["attributes"]["displayname"][0].split(" ")[0]

    preferences = []
    if auth.is_authenticated():
        user_info = auth.authenticate()
        preferences_dict = database.get_user_prefs(user_info["user"])
        preferences = []
        if preferences_dict is None:
            database.set_user_prefs(username, False, False, False, False, False)
            preferences_dict = database.get_user_prefs(user_info["user"])
        for pref in ["halal", "veg", "glutenfree", "dairyfree", "peanutfree"]:
            if preferences_dict.get(pref):
                tag = (
                    "vegan-vegetarian"
                    if pref == "veg"
                    else pref.replace("glutenfree", "gluten-free")
                    .replace("dairyfree", "dairy-free")
                    .replace("peanutfree", "peanut-free")
                )
                preferences.append(tag)

    # determine current meal
    curhour = datetime.datetime.now().hour
    if curhour < 9:
        curMeal = "Breakfast"
    elif curhour < 14:
        curMeal = "Lunch"
    else:
        curMeal = "Dinner"

    halls = [["Roma"], ["Forbes"], ["WB"], ["YN"], ["CJL"], ["Grad"]]
    random.shuffle(halls)

    best_dhall = None

    # find dining hall with most preferred meals
    for hall in halls:
        meals_list = asyncio.run(scrapedining.get_meal_info(hall, None, curMeal))
        meals_list_withPref = scrapedining.filter_meals(meals_list, tags=preferences)
        if len(meals_list_withPref) >= 3:
            best_dhall = hall
            break

    # fetch and filter meals for the best hall
    if best_dhall is not None:
        filtered_meals = scrapedining.filter_meals(meals_list, tags=preferences)

        fav_meals = database.get_fav_meals(username)
        for meal in meals_list:
            meal["is_fav"] = meal["name"] in fav_meals

        grouped_meals = defaultdict(list)
        for meal in filtered_meals:
            grouped_meals[meal["dhall"]].append(meal)

        dhall = next(iter(grouped_meals))
        return flask.render_template(
            "dashboard.html",
            hall=dhall,
            mealtime=curMeal,
            totalMeals=len(filtered_meals),
            grouped_meals=grouped_meals,
            username=username,
            userFirstname=userFirstname,
        )

    else:
        return flask.render_template(
            "dashboard.html",
            hall="Null",
            mealtime=curMeal,
            totalMeals="Null",
            grouped_meals="Null",
            username=username,
            userFirstname=userFirstname,
        )


# Find Meals Page
@app.route("/find_meals")
def find_meals():
    vegan_vegetarian = False
    halal = False
    gluten_free = False
    dairy_free = False
    peanut_free = False

    username = None
    if auth.is_authenticated():
        user_info = auth.authenticate()
        username = user_info["user"]
        preferences = database.get_user_prefs(username)
        if preferences:
            vegan_vegetarian = preferences.get("veg", False)
            halal = preferences.get("halal", False)
            gluten_free = preferences.get("glutenfree", False)
            dairy_free = preferences.get("dairyfree", False)
            peanut_free = preferences.get("peanutfree", False)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    maxdate = datetime.datetime.now() + datetime.timedelta(days=6)
    formatted_maxdate = maxdate.strftime("%Y-%m-%d")

    return flask.render_template(
        "find_meals.html",
        username=username,
        vegan_vegetarian=vegan_vegetarian,
        halal=halal,
        gluten_free=gluten_free,
        dairy_free=dairy_free,
        peanut_free=peanut_free,
        today=today,
        maxdate=formatted_maxdate,
    )


# Meals List Page
@app.route("/meals_list", methods=["GET"])
def meals_list():
    diningHall = flask.request.args.get("DHfilter", "").split(",")
    mealTimes = flask.request.args.get("MTfilter", "").split(",")
    preferences = flask.request.args.get("ARfilter", "").split(",")
    date = flask.request.args.get("date")
    print(diningHall)
    print(mealTimes)
    print(preferences)
    print(date)

    if preferences == [""]:
        preferences = []

    meals_list = asyncio.run(scrapedining.get_meal_info(diningHall, date, mealTimes[0]))
    filtered_meals = scrapedining.filter_meals(meals_list, tags=preferences)

    username = None
    if auth.is_authenticated():
        username = flask.session.get("user_info")["user"]
        veg = "vegan-vegetarian" in preferences
        halal = "halal" in preferences
        glutenfree = "gluten-free" in preferences
        dairyfree = "dairy-free" in preferences
        peanutfree = "peanut-free" in preferences
        database.set_user_prefs(username, veg, halal, glutenfree, dairyfree, peanutfree)

        fav_meals = database.get_fav_meals(username)
        for meal in meals_list:
            meal["is_fav"] = meal["name"] in fav_meals

    grouped_meals = defaultdict(list)
    for meal in filtered_meals:
        grouped_meals[meal["dhall"]].append(meal)

    print(preferences)
    return flask.render_template(
        "meals_list.html",
        grouped_meals=grouped_meals,
        preferences=preferences,
        mealtimes=mealTimes,
        dininghalls=diningHall,
        username=username,
    )


# -----------------------------------------------------------------------


@app.route("/updatefav", methods=["GET"])
def updatefav():
    if not auth.is_authenticated():
        return

    username = flask.session.get("user_info")["user"]
    meal_name = flask.request.args.get("name")

    if database.is_fav_meal(username, meal_name):
        database.remove_fav_meal(username, meal_name)
    else:
        database.add_fav_meal(username, meal_name)

    return flask.Response(status=200)


# -----------------------------------------------------------------------


# CAS Authentication Logic
@app.route("/logincas", methods=["GET"])
def logincas():
    # authenticate for side-effects, but we don't need to keep the return value
    auth.authenticate()
    return flask.redirect(flask.url_for("dashboard"))


@app.route("/logoutcas", methods=["GET"])
def logoutcas():
    logout_url = (
        auth._CAS_URL
        + "logout?service="
        + auth.urllib.parse.quote(re.sub("logoutcas", "logoutapp", flask.request.url))
    )
    flask.abort(flask.redirect(logout_url))


@app.route("/logoutapp", methods=["GET"])
def logoutapp():
    flask.session.clear()
    return flask.redirect(flask.url_for("home"))


# -----------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8000)
