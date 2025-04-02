# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

import flask
from flask import render_template
from scrapedining import get_meal_names

app = flask.Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/find_meals")
def find_meals():
    return render_template("find_meals.html")


@app.route("/meals_list", methods=["GET"])
def meals_list():
    diningHall = flask.request.args.get("DHfilter").split(",")
    mealTimes = flask.request.args.get("MTfilter").split(",")

    return render_template(
        "meals_list.html", meals=get_meal_names(diningHall, None, mealTimes[0])
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
