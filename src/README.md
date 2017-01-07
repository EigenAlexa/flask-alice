# Alice - AIML Interpreter for Alexa
This folder contains code to interpret [AIML files](http://www.alicebot.org/aiml.html).

Before proceeding, you'll need to add AIML files into `src/aiml/`. They are ignored by the repo because they are typically rather large. [Here is the download link](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/aiml-en-us-foundation-alice/aiml-en-us-foundation-alice.v1-9.zip) for the English knowledge base. Alternatively, you can find other [knowledge bases here](http://www.alicebot.org/downloads/sets.html)

## Setting up Zappa Deploy
Zappa makes it easy to deploy flask apps to Lambda containers. In our case, our zappa config is defined in zappa_settings.json.

You should watch [this video](https://www.youtube.com/watch?v=mjWV4R2P4ks) on how to deploy flask-ask in zappa if this is your first time deploying to Zappa

TODO try zappa deploy on someone else's computer
