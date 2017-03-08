from __future__ import print_function, division
from MeteorClient import MeteorClient, MeteorClientException
from alice import Alice
import time, random
from utils import func_wrap, replace_localhost
import threading

class MessageHandlerThread(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self, target=self.handle_message)
        self.daemon = True
	self.message_received = False
	self.convo_updated = False
        self.bot = bot
    def handle_message(self):
        while True:
            while not self.convo_updated or not self.message_received:
                pass
            self.bot.restart_idler()
            self.bot.respond()
            self.message_received = False
            self.convo_updated = False
            self.run()

class BotWrapper:
    def __init__(self, url, max_turns=10,callback=None, callback_params=1, msg_q=False):
        print('starting service')
        self.start_proba = 0.85
        self.url = replace_localhost(url)
        self.bot = Alice()
        self.max_turns = max_turns
        self.sending_message = False
        self._id = None
        self.use_msg_q = msg_q # msg_q sets whether or not we are queueing messages
        websocket = 'ws://%s/websocket' % self.url
        self.client = MeteorClient(websocket)
        self.client.connect()

        self.idle_time = 3 * 60
        self.thread_time = 2
        self.max_retry = 3

    def restart_idler(self):
        ''' Restarts the idle watcher '''
        print('restarting idler')
        if hasattr(self,'idler_thread') and self.idler_thread:
            self.idler_thread.cancel()
        self.idler_thread = threading.Timer(self.idle_time, self.idle_user_handler)
        self.idler_thread.start()

    def idle_user_handler(self):
        """ Handler that disconnects conversation in the event that a user leaves """

        print('user is idle disconnect')
        self.idler_thread = None
        self.end_convo()

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
        # TODO make this into threading timers.
        while not self._id:
            self.client.login(user, pwd, callback= func_wrap(
                set_user, params=1))
            time.sleep(0.5)

    def logout(self):
        self.client.logout()

    def find_and_join_room(self):
        """ Finds a room and joins it """
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
            print("subscribing to {}".format(collection))
            self.client.subscribe(collection, params, callback)
        except MeteorClientException:
            print('Already subscribed to {}. Running callback with None'.format(collection))
            if callback:
                callback(None)

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

        self.client.call('users.exitConvo', [self._id]);
        self.client.call('convos.updateRatings', [self.roomId, self._id, 'not']);
        self.available = True
        if self.idler_thread:
            self.idler_thread.cancel()

    def set_wpm(self):
        """ Set the words per minute of the bot """
        wpm = random.randint(90,140)
        self.cps = 60 / (wpm * 5)
        print('Setting wpm : {} '.format(wpm))

    def prime_bot(self,convo_obj):
        """  the conversational bot """
        print('convo_obj',convo_obj)
        input_msg = 'hi'
        if 'msgs' in convo_obj and convo_obj['msgs']:
            topic_msg_id = convo_obj['msgs'][0]
            msg_obj = self.client.find_one('messages', selector={'_id': topic_msg_id})
            if msg_obj:
                input_msg = msg_obj['message']

        msg = self.bot.message(input_msg, self.roomId)
        if random.random() > self.start_proba:
            self.send_message(msg)

    def watch_room(self, roomId, callback=None):
        """
        Setup Event Listeneres for a room and checks to make sure that the room is updating
        """
        self.turns = 0
        convo_obj = self.client.find_one('convos', selector={'_id' : roomId})
        self.room_closed = convo_obj['closed']
        self.set_wpm()

        self.last_message = ""
        self.confirmed_messages = [] # all messages sent by the user that have been confirmed
        self.thread = MessageHandlerThread(self)
        def message_added(collection, id, fields):
            """ callback for when a message is added """
            if (collection == 'messages' and 'message' in fields and 'user' in fields):
                print(type(self._id), type(fields['user']), self._id, fields['user'])
                if fields['user'] != self._id and self.last_message != fields['message']:
                    self.restart_idler()
                    self.receive_message(fields['message'])
                    self.last_message = fields['message']
                    self.thread.message_received = True
                elif fields['user'] == self._id:
                    print('\t messages from self detected')
                    self.confirmed_messages.append(fields['message'])

        self.client.on('added', message_added)

        def watch_convo(collection, id, fields, cleared):
            """ callback for when any part of the conversation is updated """
            if self.roomId and collection == "convos" and id == self.roomId:
                # print('\t',fields)
                if 'closed' in fields:
                    print('\tRoom is closed: ', fields['closed'])
                    self.room_closed = fields['closed']
                    self.end_convo()
                if 'msgs' in fields:
                    print('\tMessages updated in convo "{}"'.format(id))
                    # TODO this is bugggy
                    self.thread.convo_updated = True
                if 'turns' in fields:
                    print('\tTurns updated to "{}"'.format(fields['turns']))
                    self.turns = fields['turns']
            elif self.roomId == id:
                print(collection, id, fields)

        self.client.on('changed', watch_convo)
        # mark the bot as ready to talk
        self.client.call('convos.makeReady', [roomId, self._id])
        self.restart_idler()
        self.prime_bot(convo_obj)
        print("before thread")
        self.thread.start()
        print("after thread")

        if callback:
            callback(None)

    def respond(self):
        """ Kind of a hacky way to respond to the conversation """
        print("responding")
        if self.msg_queue and self.use_msg_q:
            partner_msg = self.msg_queue[0]
            self.msg_queue = self.msg_queue[1:]
            msg = self.bot.message(partner_msg, self.roomId)
            print(msg)
            self.send_message(msg)

        if self.msg_queue and not self.sending_message:
            partner_msg = self.msg_queue[-1]
            self.msg_queue = self.msg_queue[:-1]
            msg = self.bot.message(partner_msg, self.roomId)
            print(msg)
            self.send_message(msg)

    def still_in_conv(self):
        """ Returns whether the conversation is still moving """
        in_conv = self.roomId != None and not self.client.find_one('convos', selector={'_id' : self.roomId})['closed']
        print('\tstill in conv', in_conv )
        if not in_conv:
            self.end_convo()
        print('\tclosed: ',self.client.find_one('convos', selector={'_id': self.roomId})['closed'])
        return in_conv

    def get_convo_dict(self):
        if self.roomId:
            return self.client.find_one('convos', selector={'_id': self.roomId})
        else:
            return {}

    def get_message(self,idx):
        ''' Returns the message at idx'''
        convo_dict = self.get_convo_dict()
        if convo_dict:
            topic_msg_id = convo_dict['msgs'][idx]
            msg_dict = self.client.find_one('messages', selector={'_id': topic_msg_id})
            # print(msg_dict)
            if msg_dict:
                return msg_dict['message']
        return ''

    def received_message(self, message):
        """ Checks whether the bot actually sent the message """
        # TODO add handler that removes a confirmed message to save memory
        return message in self.confirmed_messages

    def retry_message(self, message, retry=0, callback=None):
        """ Handler that makes attempts to connect a user back into a conversation """
        # TODO set as properties
        if retry == 0 or not self.received_message(message) and retry < self.max_retry:
            self.update_conversation(message, callback)

            if retry != 0: print('\t\tRetry {} of sending "{}"'.format(retry, message))

            t = threading.Timer(self.thread_time, lambda : self.retry_message(message, retry + 1))
            t.start()
        elif retry >= self.max_retry:
            print('\tMax retries reached - couldn\'t verify whether {} was received'.format(message))
        else:
            print('\t"{}" successfully received'.format(message))

    def update_conversation(self, message, callback=None):
        self.client.call('convos.updateChat', [message, self.roomId, self._id], callback)

    def _send_message(self, message, callback=None):
        self.last_message_sent  = message
        if self.still_in_conv():
            self.retry_message(message, callback=callback)
        else:
            print('Not responding - conversation is OVER')
        self.sending_message = False

    def send_message(self, message, callback=None):
        # calculates typing speed based on rough cps for user
        sleep_time = self.cps * len(message)
        print("Preparing to send '{}' Waiting '{}' seconds.".format(message, sleep_time))
        t = threading.Timer(sleep_time, lambda: self._send_message(message,callback))
        t.start()

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
