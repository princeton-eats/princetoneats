# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

import flask
import dotenv
import os
from scrapedining import get_meal_info
import auth
import re

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
    return flask.render_template("find_meals.html")


@app.route("/meals_list", methods=["GET"])
def meals_list():
    diningHall = flask.request.args.get("DHfilter").split(",")
    mealTimes = flask.request.args.get("MTfilter").split(",")

    mealsDict = get_meal_info(diningHall, None, mealTimes[0])

    return flask.render_template("meals_list.html", mealsDict=mealsDict, currDH="")


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
