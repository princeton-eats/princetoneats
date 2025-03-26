# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

from flask import Flask, render_template
from scrapedining import get_meal_names

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/find_meals")
def find_meals():
    return render_template("find_meals.html")


@app.route("/meals_list")
def meals_list():
    hall = "r"
    meal = "Breakfast"
    return render_template("meals_list.html", meals=get_meal_names(hall, None, meal))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
