# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

import flask
import dotenv
import os
import scrapedining
import auth
import re
import datetime
from collections import defaultdict

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
    username = None if user_info is None else user_info["user"]
    userFirstname = (
        None
        if user_info is None
        else user_info["attributes"]["displayname"][0].split(" ")[0]
    )

    if auth.is_authenticated():
        user_info = auth.authenticate()
        preferences_dict = database.get_user_prefs(user_info["user"])
        preferences = []
        for pref in ["halal", "veg", "glutenfree", "dairyfree", "peanutfree"]:
            if preferences_dict[pref]:
                if pref == "veg":
                    pref = "vegan-vegetarian"
                preferences.append(pref)

    # if auth.is_authenticated():
    #     user_info = auth.authenticate()
    #     preferences = database.get_user_prefs(user_info["user"])

    halls = [["Roma"], ["Forbes"], ["WB"], ["YN"], ["CJL"], ["Grad"]]
    maxMeals = 0
    curMeal = ""
    bestDining = "hairline"

    # can make this better
    curhour = datetime.datetime.now().hour

    if curhour < 9:
        curMeal = "Breakfast"
    elif curhour >= 9 and curhour < 14:
        curMeal = "Lunch"
    elif curhour >= 14:
        curMeal = "Dinner"

    for i in range(0, len(halls)):
        meals_list = scrapedining.get_meal_info(halls[i], None, curMeal)
        meals_list_withPref = scrapedining.filter_meals(meals_list, tags=preferences)
        meal_list_len = len(meals_list_withPref)
        print(meal_list_len)
        if meal_list_len > maxMeals:
            maxMeals = meal_list_len
            bestDining = halls[i]

    print(bestDining)
    if bestDining != "hairline":
        meals_list = scrapedining.get_meal_info(bestDining, None, curMeal)
        # print(f"Found {len(meals_list)} total meals")
        # print(f"Filtering with preferences: {preferences}")
        filtered_meals = scrapedining.filter_meals(meals_list, tags=preferences)
        # print(f"After filtering, {len(filtered_meals)} meals remain")
        for meal in meals_list:
            meal["is_fav"] = database.is_fav_meal(username, meal["name"])

        grouped_meals = defaultdict(list)
        for meal in filtered_meals:
            grouped_meals[meal["dhall"]].append(meal)
            # dhallFinal = grouped_meals[meal["dhall"]]

        print(grouped_meals)
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
            hall=bestDining,
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
    user_info = flask.session.get("user_info")

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


# -----------------------------------------------------------------------


# Meals List Page
@app.route("/meals_list", methods=["GET"])
def meals_list():
    diningHall = flask.request.args.get("DHfilter", "").split(",")
    mealTimes = flask.request.args.get("MTfilter", "").split(",")
    preferences = flask.request.args.get("ARfilter", "").split(",")

    if len(preferences[0]) == 0:
        preferences = []

    meals_list = scrapedining.get_meal_info(diningHall, None, mealTimes[0])
    print(f"Found {len(meals_list)} total meals")
    print(f"Filtering with preferences: {preferences}")
    filtered_meals = scrapedining.filter_meals(meals_list, tags=preferences)
    print(f"After filtering, {len(filtered_meals)} meals remain")

    username = None
    if auth.is_authenticated():
        username = flask.session.get("user_info")["user"]

        veg = "vegan-vegetarian" in preferences
        halal = "halal" in preferences
        glutenfree = "gluten-free" in preferences
        dairyfree = "dairy-free" in preferences
        peanutfree = "peanut-free" in preferences
        database.set_user_prefs(username, veg, halal, glutenfree, dairyfree, peanutfree)

        for meal in meals_list:
            meal["is_fav"] = database.is_fav_meal(username, meal["name"])

    grouped_meals = defaultdict(list)
    for meal in filtered_meals:
        grouped_meals[meal["dhall"]].append(meal)

    return flask.render_template(
        "meals_list.html", grouped_meals=grouped_meals, username=username
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

    print(meal_name)
    print(database.is_fav_meal(username, meal_name))

    return flask.Response(200)


# -----------------------------------------------------------------------


# CAS Authenitcation Logic
@app.route("/logincas", methods=["GET"])
def logincas():
    # Log in to CAS and redirect home
    user_info = auth.authenticate()
    username = user_info["user"]
    print(username)
    return flask.redirect(flask.url_for("dashboard"))


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


# -----------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8000)
