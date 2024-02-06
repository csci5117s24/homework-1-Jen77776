from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<p>Welcome to the Survey!</p>"

@app.route("/survey")
def survey():
    return "<p>Survey Page</p>"

@app.route("/decline")
def decline():
    return "<p>Decline Page</p>"

@app.route("/thanks")
def thanks():
    return "<p>Thank You Page</p>"

@app.route("/api/results")
def results():
    return "<p>API Results</p>"

if __name__ == "__main__":
    app.run(debug=True)
