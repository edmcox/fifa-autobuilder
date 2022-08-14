from flask import Flask, request, render_template
from optimiser import chemistry_checker

app = Flask(__name__)


@app.route("/")
def form():
    return render_template("form.html")


@app.route("/", methods=["POST"])
def form_post():
    squad_link = request.form["FUTBIN Squad Link"]
    top_n = request.form.get("top_n")
    subs = request.form.get("subs")

    squads = chemistry_checker(squad_link, top_n=int(top_n), subs=bool(subs))

    if isinstance(squads, str):
        return squads

    return render_template(
        "plot.html", poss_combs=str(squads), url="/static/images/plot.png"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
