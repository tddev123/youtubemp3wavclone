from flask import Blueprint, render_template, request, jsonify, redirect, url_for

views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("youtubetowavfrontend.html", name="Joe")

@views.route("/pythonprojects")
def projects():
    return render_template("pythonprojects.html")



@views.route("/profile")
def profile():
    args = request.args
    name = args.get('name')
    return render_template("index.html", name=name)

@views.route("/json")
def get_json():
    return jsonify({'name': 'tim', 'coolness': 10})

@views.route("/data")
def get_data():
    dat = request.json
    return jsonify('data')

@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.home"))

@views.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@views.route("/hamstrings")
def hamstrings():
    return render_template("hamstring.html")

@views.route("/biceps")
def biceps():
    return render_template("biceps.html")


@views.route("/chest")
def chest():
    return render_template("chest.html")

@views.route("/1-4_days")
def l4hams():
    return render_template("hamstrings1-4days.html")

@views.route("tutcalculator")
def tutcal():
    return render_template("tut.html")

@views.route("tutcalc")
def tutcalc():
    return render_template(tutcalc.html)


@views.route("stopwatch")
def stopwatcch():
    return render_template("stopwatchpage.html")

@views.route("calendar")
def calendarr():
    return render_template("datacalendar.html")
