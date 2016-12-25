import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_session():
    welcome_msg = render_template('hello')
    return statement(welcome_msg)

@ask.intent("AllIntent", convert={'All': str})
def next_round(All):
    response = All # TODO make this interact with the AIML interpretor
    # reponse = render_template('respond', response=response) # TODO delete if not necessary
    return statement(response)

if __name__ == '__main__':
    app.run(debug=True)
