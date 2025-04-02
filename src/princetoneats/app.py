# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

# from flask import Flask, render_template, session
import flask
import dotenv
import os

from scrapedining import get_meal_names

# -----------------------------------------------------------------------

from top import app

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
    return flask.render_template("find_meals.html")


@app.route("/meals_list")
def meals_list():
    hall = "r"
    meal = "Breakfast"
    return flask.render_template(
        "meals_list.html", meals=get_meal_names(hall, None, meal)
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
