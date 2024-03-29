""" The main file for the bot server. """
from __future__ import print_function
import json
from flask import Flask, request
from bot_wrapper import BotWrapper
from MeteorClient import MeteorClient
from utils import replace_localhost
import atexit
# create our little application :)
app = Flask(__name__)
running_bots = []
room_ids = set()

@app.cli.command('cli')
def cli_command():
    # TODO determien use
    """Runs when the cli command above is run"""
    print('cli comand here')

magic_phrase = []

@app.before_first_request
def on_start():
    """ only used for debugging """
    print('on start')

@app.teardown_appcontext
def teardown_func(error):
    """Runs on teardown"""
    pass

@app.route('/get-bot', methods=['POST'])
def start_bot():
    global magic_phrase
    print(type(request.data))
    reqdata = json.loads(request.data)
    magic_phrase = [reqdata['magic_phrase']]
    server_url = reqdata['server_url']
    room_id = reqdata['room_id']
    otherUserId = reqdata['other_user']
    print(reqdata)
    if room_id not in room_ids:
        # max_turns = reqdata['max_turns']
        # checks that bots are running
        def get_bot_cb(bot):
            bot.join_room(room_id, otherUserId)
        bot = get_bot(server_url, callback=
                get_bot_cb)
        print(bot)
        room_ids.add(room_id)
        return 'New bot starting in room "{}"'.format(room_id)
    else:
        return 'Bot already started in room "{}"'.format(room_id)


def get_bot(server_url, callback=None):
    ''' returns a running bot or None otherwise '''
    avail_bots = find_available_bots(server_url)
    if avail_bots:
        bot =  avail_bots[0]
        if callback:
            callback(bot)
        return bot
    else:
        print('making a new bot')
        # makes a new bot if none are available
        return make_new_bot(server_url, callback=
                callback)

def find_available_bots(server_url):
    ''' returns all bots that can be added to a room '''
    avail_bots = [r for r in running_bots if r.available and r.url == server_url]
    print('running bot: {}; bots available: {}'.format(len(running_bots), len(avail_bots)))
    return avail_bots

def get_new_login(server_url, callback=None):
    """ queries the server to give a new login"""
    server_url = replace_localhost(server_url)
    # connects to the server
    websocket = 'ws://%s/websocket' % server_url
    client = MeteorClient(websocket)
    client.connect()
    def cb(error, data):
        client.close()
        if callback:
            callback(error, data)
    # queries the method with a magicphrase
    client.call('getBotUsername', magic_phrase, cb)

def make_new_bot(server_url, callback=None):
    ''' make a new bot connected to the server url '''
    global magic_phrase
    bot = BotWrapper(server_url, magic_phrase[0])

    def login_callback(error, data):
        if (error):
            print('error on login callback', error)
        else:
            print('login callback data', data)
            next_user = data
            print(next_user)
            bot.login(next_user['user'], next_user['pwd'], callback, callback_params=1)
            running_bots.append(bot)


    get_new_login(server_url, login_callback)
    return bot

def end_all_bots():
    print('closing all bots')
    for bot in running_bots:
        print(bot._id, 'closing connection')
        if not bot.available:
            bot.end_convo()
        bot.client.close()

atexit.register(end_all_bots)

if __name__ == "__main__":
    make_new_bot('localhost:3000')
