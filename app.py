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
    welcome_msg = "hello"
    return statement(welcome_msg)

@ask.intent("AllIntent", convert={'All': str})
def next_round(All):
    response = alice.message(All)
    # TODO make a handler to detect whether a question has been asked
    # can't reprompt here because this is after the fact
    return question(response)

@ask.intent("AMAZON.StopIntent")
def stop():
    return statement("goodbye")

@ask.intent("AMAZON.HelpIntent")
def help():
	return statement("good luck.")

@ask.session_ended
def session_ended():
    return statement("")
if __name__ == '__main__':
    app.run(debug=True)
