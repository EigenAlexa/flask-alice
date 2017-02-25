from __future__ import print_function
from MeteorClient import MeteorClient
from alice import Alice

def func_wrap(func, params=0):
	def return_func(error, data):
		if error:
			print(error)
		elif params == 0:
			func()
		elif params == 1:
			func(data)

	return return_func


class BotWrapper:
	def __init__(self, url):
		print('starting service')
		self.url = url
		# self.client = MeteorClient(
		self.client = MeteorClient('ws://%s/websocket' %url)
		self.client.connect()
		self.login()

		# setup alice
		self.bot = Alice()

	def login(self):
		def callback(error, data):
			print('calling back')
			if not error:
				self.set_user_id(data['id'])
				print(self._id)
			else:
				print('error')
				print(error)
		print('logging in')
		self.client.login('notbot','botbot', callback= func_wrap(
			lambda data : self.set_user_id(data['id']), params=1))

	def logout(self):
		self.client.logout()
	def run(self):
		self.find_room(self, callback=
				lambda roomId : self.join_room(roomId))

	def find_room(self, callback=None):
		self.client.subscribe('openrooms')
		self.client.subscribe('currentUser',params=[self._id])
		user = self.client.find_one('users')

		if user.in_convo:
			roomId = user.curConvo
		else:
			openrooms = self.client.find('convos') # {curSessions : {$lt  :2}}
			roomId = openrooms[0] if openrooms and len(openrooms) > 0 else -1

		if roomId != -1:
			# Add user to room
			self.client.call('convos.addUserToRoom', params=[self._id, roomId], callback=
					func_wrap(lambda : callback(roomId)))

	def join_room(self, roomId, callback=None):
		""" join a room based on roomId """
		self.roomId = roomId
		self.client.subscribe('chat', [roomId], func_wrap(
			lambda : self.client.subscribe('msgs', [roomId], func_wrap(
				lambda : self.client.subscribe('currentUsers', [roomId], callback)) )))
	def watch_room(self, roomId, callback=None):
	""" Watch room and make sure that the room is updating """
	## TODO get catch for change in messages
		def added(collection, id, fields):
		print('* ADDED {} {}'.format(collection, id))
		for key, value in fields.items():
		print('  - FIELD {} {}'.format(key, value))
		self.client.on('added', added)

	def send_message(self, message, callback=None):
		self.client.call('convos.updateChat', [message, self.roomId, self._id], callback)

	def receive_message(self, message):
		""" Called whenever the bot receives a message """
		# TODO add wait time between message reeived and message sent
		self.send_message(self.bot.message(message))

	def set_user_id(self, id):
		self._id = id
url = "127.0.0.1:3000"
bot = BotWrapper(url)
# print(bot._id)
