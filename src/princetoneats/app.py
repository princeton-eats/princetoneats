# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

# from flask import Flask, render_template, session
import flask
import dotenv
import os

from scrapedining import get_meal_names
import auth

# -----------------------------------------------------------------------

app = flask.Flask(__name__)

dotenv.load_dotenv()
app.secret_key = os.environ["APP_SECRET_KEY"]

# -----------------------------------------------------------------------


@app.route("/")
def home():
    return flask.render_template("index.html")


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


@app.route("/signin")
def sign_in():
    user_info = auth.authenticate()
    username = user_info["user"]
    print(username)
    return flask.redirect(flask.url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
