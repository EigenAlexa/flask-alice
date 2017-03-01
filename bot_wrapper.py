from __future__ import print_function, division
from MeteorClient import MeteorClient, MeteorClientException
from alice import Alice
import time, random
from utils import *
class BotWrapper:
    def __init__(self, url, max_turns=10,callback=None, callback_params=1, msg_q=False):
        print('starting service')
        self.url = replace_localhost(url)
        self.bot = Alice()
        self.max_turns = max_turns
        self.sending_message = False
        self._id = None
        self.use_msg_q = msg_q # msg_q sets whether or not we are queueing messages
        websocket = 'ws://%s/websocket' % self.url
        print(websocket)
        self.client = MeteorClient(websocket)
        self.client.connect()
        # self.anon_login(callback, callback_params)
        # self.login(callback, callback_params)
    def anon_login(self, callback=None, callback_params=1):
        """ TODO doesn't work because anon users need client side calls -methods i dont' have access to """

        # DON"T USE
        print('anon login')
        def set_user(data):
            print(data)
            user = self.client.find_one('users')
            if user:
                print('login user', user._id)
                self.set_user_id(user._id)
                self.unsubscribe('getUserId')
            if callback and callback_params == 1:
                callback(self)
            elif callback:
                callback()

        self.subscribe('getUserId', callback=
                func_wrap(set_user, params=1))

    def login(self, user='notbot', pwd='botbot', callback=None, callback_params=0):
        print('logging in')

        def set_user(data):
            self.set_user_id(data['id'])
            print('user id set to', self._id)
            if callback and callback_params == 1:
                print('running callback with 1 parameter')
                callback(self)
            elif callback and callback_params == 0:
                callback()

        while not self._id:
            self.client.login(user, pwd, callback= func_wrap(
                set_user, params=1))
            time.sleep(0.5)

    def logout(self):
        self.client.logout()

    def find_and_join_room(self):
        self.find_room(callback=(lambda roomId : self.join_room(roomId)))

    def find_room(self, callback=None):
        print('looking for an open room')
        def room_callback():
            print('looking for a room')
            user = self.client.find_one('users')
            print('user dict',user.items())
            if user["in_convo"]:
                roomObj = user["curConvo"]
                print('roomid: ', roomObj)
            else:
                openrooms = self.client.find('convos') # {curSessions : {$lt  :2}}
                roomObj = openrooms[0] if openrooms and len(openrooms) > 0 else -1

            # TODO may have issues with room id when user is in convo
            if roomObj != -1:
                if type(roomObj) == str:
                    print(roomObj, 'room')
                    print('openrooms', openrooms)
                callback(roomObj['_id'])
                # Add user to room

            else:
                print('No rooms found. Back to the bat cave')
        self.subscribe('openrooms', callback=func_wrap(
            lambda : self.subscribe('currentUser',params=[self._id], callback=func_wrap(
                lambda : room_callback()
            )
        )))

    def subscribe(self, collection, params=[], callback=None):
        """ Wrapper for subscribe to avoid issues with already subscribed rooms """
        try:
            self.client.subscribe(collection, params, callback)
        except MeteorClientException:
            print('Already subscribed to {}. Running callback with None'.format(collection))
            if callback:
                callback(None)

    def join(self, roomId):
        """ Shortcut to join without callback """
        self.join_room(roomId)

    def join_room(self, roomId, callback=None):
        """ Join a room based on roomId """
        print ('join room with id', roomId)
        self.roomId = roomId
        self.msg_queue = []
        self.available = False

        self.client.call('convos.addUserToRoom', params=[self._id, roomId], callback= func_wrap(
            lambda : self.subscribe('chat', [roomId], func_wrap(
                lambda : self.subscribe('msgs', [roomId], func_wrap(
                    lambda : self.subscribe('currentUsers', [roomId], func_wrap(
                        lambda: self.watch_room(roomId, callback)) )
                    )
                )
            ) )
        ))

    def unsubscribe(self, collection):
        """ Unsubscribe from the collection """
        try:
            self.client.unsubscribe(collection)
        except MeteorClientException:
            print('\t"{}" not subscribed to.'.format(collection))

    def end_convo(self):
        """ End the conversation """
        print('end conversation and unsubscribe from it all')
        self.client.remove_all_listeners('added')
        self.client.remove_all_listeners('changed')

        self.unsubscribe('chat')
        self.unsubscribe('msgs')
        self.unsubscribe('currentUsers')

        self.client.call('convos.updateRatings', [self.roomId, self._id, 'not']);
        self.available = True

    def watch_room(self, roomId, callback=None):
        """ Watch room and make sure that the room is updating """
        self.turns = 0
        convo_obj = self.client.find_one('convos', selector={'_id' : roomId})
        print(convo_obj, 'convo_obj')
        self.room_closed = convo_obj['closed']
        # prompt text removed so this is commented out
        # self.topic = convo_obj['promptText']

        # # prime the bot with the current topic
        # self.bot.message(self.topic, self.roomId)

        self.client.call('convos.makeReady', [roomId, self._id])
        wpm = random.randint(50,100)
        self.cps = 60 / (wpm * 5)
        self.last_message = ""
        print('Setting wpm : {} '.format(wpm))
        if random.random() > 0.5:
            msg = self.bot.message('hi', self.roomId)
            self.send_message(msg)
        def message_added(collection, id, fields):
            if ('message' in fields and 'user' in fields and fields['user'] != self._id):
                if self.last_message != fields['message']:
                    self.receive_message(fields['message'])
                    self.last_message = fields['message']

        self.client.on('added', message_added)

        def watch_convo(collection, id, fields, cleared):
            if self.roomId and collection == "convos" and id == self.roomId:
                # print('\t',fields)
                if 'closed' in fields:
                    print('\tRoom is closed: ', fields['closed'])
                    self.room_closed = fields['closed']
                    self.end_convo()
                if 'msgs' in fields:
                    print('\tMessages updated in convo "{}"'.format(id))
                    self.respond()
                if 'turns' in fields:
                    print('\t Turns updated to "{}"'.format(fields['turns']))
                    self.turns = fields['turns']
        self.client.on('changed', watch_convo)
        if callback:
            callback(None)

    def respond(self):
        """ Kind of a hacky way to respond to the conversation """
        if self.msg_queue and self.use_msg_q:
            partner_msg = self.msg_queue[0]
            self.msg_queue = self.msg_queue[1:]
            msg = self.bot.message(partner_msg, self.roomId)
            self.send_message(msg)

        if self.msg_queue and not self.sending_message:
            partner_msg = self.msg_queue[-1]
            self.msg_queue = self.msg_queue[:-1]
            msg = self.bot.message(partner_msg, self.roomId)
            self.send_message(msg)

    def still_in_conv(self):
        """ Returns whether the conversation is still moving """
        in_conv = self.roomId != None and self.turns < self.max_turns and not self.client.find_one('convos', selector={'_id' : self.roomId})['closed']
        print('\tstill in conv', in_conv )
        if not in_conv:
            self.end_convo()
        print('\tclosed: ',self.client.find_one('convos', selector={'_id': self.roomId})['closed'])
        return in_conv


    def send_message(self, message, callback=None):
        # calculates typing speed based on rough cps for user
        time.sleep(self.cps * len(message))
        if self.still_in_conv():
            print("Sending '{}'".format(message))
            self.client.call('convos.updateChat', [message, self.roomId, self._id], callback)
        else:
            print('Not responding - conversation is OVER')
        self.sending_message = False

    def receive_message(self, message):
        """ Called whenever the bot receives a message """
        print('Received "{}"'.format(message))
        self.msg_queue.append(message)
        # message = 'sup then' # self.bot.message(message)

        # self.send_message(message)

    def set_user_id(self, id):
        self.available = True
        print('set user id to ', id)
        self._id = id
if __name__ == "__main__":
    url = "127.0.0.1:3000"
    bot = BotWrapper(url)
# print(bot._id)
# bot.run()
# bot.logout()
