from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    data = [
        ("01-01-2020", 1597),
        ("02-01-2020", 1456),
        ("03-01-2020", 1908),
        ("05-01-2020", 896),
        ("06-01-2020", 755),
        ("07-01-2020", 453),
        ("09-01-2020", 1100),
        ("09-01-2020", 1235),
        ("01-01-2020", 1478),
    ]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    print(labels)
    print(values)

    return render_template("graph.html", labels=labels, values=values)