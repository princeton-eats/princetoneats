from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/find_meals")
def find_meals():
    return render_template("find_meals.html")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
