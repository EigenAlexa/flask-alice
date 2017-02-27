import aiml
import os

class Alice:
    def __init__(self):
        DIR = os.path.dirname(os.path.realpath(__file__)) + '/aiml/'
        files = [DIR + f for f in os.listdir(DIR) if os.path.isfile(DIR + f) and '.aiml' in f]
        interpretor = aiml.Kernel()
        interpretor.verbose(False)
        # TODO uncomment when this works
        # if os.path.isfile("bot_brain.brn"):
        #     interpretor.bootstrap(brainFile = "bot_brain.brn")
        # else:
        interpretor.bootstrap(learnFiles=files)

        # interpretor.saveBrain("bot_brain.brn")
        self.interpretor = interpretor

    def message(self, string, sessionID=None):
        if sessionID:
            return self.interpretor.respond(string, sessionID)
        else:
            return self.interpretor.respond(string)

if __name__ == "__main__":
    alice = Alice()
    print alice.message("what language are you speaking")
