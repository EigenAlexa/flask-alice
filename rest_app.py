from flask import Flask, request
from alice import Alice

app = Flask(__name__)
alice = Alice()

@app.route("/", methods=["POST"])
def next_round():
    response = alice.message(request.form['text'])
     # TODO make a handler to detect whether a question has been asked
    return response#.reprompt("Hey, let's talk about something")

if __name__ == '__main__':
    app.run(debug=True, port=80, host="0.0.0.0")
