from flask import Flask, request, render_template
from optimiser import chemistry_checker

app = Flask(__name__)


@app.route("/")
def form():
    return render_template("form.html")


@app.route("/", methods=["POST"])
def form_post():
    squad_link = request.form["FUTBIN Squad Link"]
    squads = chemistry_checker(squad_link)

    if isinstance(squads, str):
        return squads

    return render_template("plot.html", url="/static/images/plot.png")


if __name__ == "__main__":
    app.run()
