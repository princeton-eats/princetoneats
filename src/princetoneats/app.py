# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

# from flask import Flask, render_template
import flask
from flask import render_template
from scrapedining import get_meal_names

app = flask.Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/find_meals")
def find_meals():
    diningHalls = flask.request.args.getlist("DHfilter")
    mealTimes = flask.request.args.getlist("MTfilter")
    print(diningHalls)
    print(mealTimes)

    linkStringDH = ""
    linkStringMT = ""
    print(mealTimes)

    for i in range(len(diningHalls)):
        linkStringDH += "DHfilter=" + diningHalls[i]
        linkStringDH += "&"

    for i in range(len(mealTimes)):
        linkStringMT += "MTfilter=" + mealTimes[i]
        if i != len(mealTimes) - 1:
            linkStringMT += "&"

    print(linkStringDH + linkStringMT)
    return render_template("find_meals.html", MT=linkStringMT, DH=linkStringDH)


@app.route("/meals_list", methods=["GET"])
def meals_list():
    diningHall = flask.request.args.getlist("DHfilter")
    mealTimes = flask.request.args.getlist("MTfilter")

    print(diningHall)

    return render_template(
        "meals_list.html", meals=get_meal_names(diningHall, None, mealTimes[0])
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
