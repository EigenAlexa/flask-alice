import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from alice import Alice

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)
alice = Alice()

@ask.launch
def new_session():
    welcome_msg = render_template('hello')
    return statement(welcome_msg)

@ask.intent("AllIntent", convert={'All': str})
def next_round(All):
    response = alice.message(All)
    return statement(response) # TODO make a handler to detect whether a question has been asked

if __name__ == '__main__':
    app.run(debug=True)
