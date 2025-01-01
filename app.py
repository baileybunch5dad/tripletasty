from flask import Flask, render_template
import numpy as np

print("Starting")
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
    labels = [str(i) for i in range(len(values))]
    print(labels)
    print(values)

    print("weibull shape 5.")
    values = [np.mean(np.random.weibull(5., 10000)) for i in range(10000)]
    # values = [int(v * 100) for v in values]
    # # print(values)
    # labels = [str(i) for i in range(len(values))]
    # # print(labels)
    # # print("render")
    # xaxis = [z for z in range(10)]
    # yaxis = [x-5 for x in range(10)]
    # # passdata = { 'x': xaxis, 'y': yaxis }
    # yaxis = [int(v) for v in values]
    # xaxis = [x for x in range(len(values))]

    hist, bin_edges = np.histogram(values, bins='auto')
    xaxis = [float(x) for x in bin_edges]
    yaxis = [int(y) for y in hist]
    print(hist)
    print(bin_edges)

    # return render_template("graph.html", labels=labels, values=values)
    return render_template("graph3.html", xlist=xaxis, ylist=yaxis)

app.run()