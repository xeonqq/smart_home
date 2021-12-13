from flask import Flask, render_template, request
from controller import Controller

app = Flask(__name__)
controller = Controller()


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.form.get('on') == 'ON':
        controller.switch_on()
    elif request.form.get('off') == 'OFF':
        controller.switch_off()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
