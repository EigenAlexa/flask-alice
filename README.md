## Using Alice with BotOrNot
'''
# if you don't have aiml in the directory
./download-aiml.sh
./start-bot-server.sh
'''

# Alice - AIML Interpreter for Alexa
**NOTE This requires python 2 and a virtualenv. It doesn't work with conda.**

This folder contains code to interpret [AIML files](http://www.alicebot.org/aiml.html).

Before proceeding, you'll need to add AIML files into `src/aiml/`. They are ignored by the repo because they are typically rather large. [Here is the download link](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/aiml-en-us-foundation-alice/aiml-en-us-foundation-alice.v1-9.zip) for the English knowledge base. Alternatively, you can find other [knowledge bases here](http://www.alicebot.org/downloads/sets.html)

## Setting up Zappa Deploy
Zappa makes it easy to deploy flask apps to Lambda containers. In our case, our zappa config is defined in zappa_settings.json. Change the project_name variable to the name you want the lambda function to have. It is case insensitive and appends "-dev" to the end of it.

You should watch [this video](https://www.youtube.com/watch?v=mjWV4R2P4ks) on how to deploy flask-ask in zappa if this is your first time deploying to Zappa

<<<<<<< HEAD
Once you've run Zappa properly, all you need to do is run
```
zappa update dev
```
Where `dev` is the name of the version you're deploying.

## Testing without a Zappa deploy
Instead of using a Zappa deploy (which can be a pain if you're trying to iterate quickly) you can just run the flask server behind an ngrok proxy. [This blog post tutorial](https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/Flask-Ask-A-New-Python-Framework-for-Rapid-Alexa-Skills-Kit-Development) contains a howto for setting up ngrok.

I've also found that it is available in brew, apt-get, and maybe is in yum/pacman as well.

When its installed, all you'll need to run is
```
ngrok http 5000
```
and follow the instructions listed in the link above
