from django.conf import settings

from .json import jsondumps
import requests
from requests.exceptions import RequestException


class RoomController(object):
	def __init__(self):
		self.room_listings = []

	def register(self, superclass):
		for view in superclass.__subclasses__():
			if view.register_for_model and view.model is not None:
				listing = getattr(view, 'get_rooms_for_user', None)

				if listing and callable(listing):
					self.room_listings.append(listing)

			self.register(view)

		return self

	def list_rooms_for_user(self, user):
		rooms = []

		for listing in self.room_listings:
			rooms += listing(user)

		return rooms


channel = None


def get_websocket_channel(force_new=False):
	import pika
	from pika import BlockingConnection
	global channel
	if channel and channel.is_open:
		if not force_new:
			return channel
		if force_new:
			try:
				channel.close()
			except ChannelWrongStateError:
				pass
			finally:
				channel = None

	connection_credentials = pika.PlainCredentials(settings.HIGH_TEMPLAR['rabbitmq']['username'],
												   settings.HIGH_TEMPLAR['rabbitmq']['password'])
	connection_parameters = pika.ConnectionParameters(settings.HIGH_TEMPLAR['rabbitmq']['host'],
													  credentials=connection_credentials)
	connection = BlockingConnection(parameters=connection_parameters)
	channel = connection.channel()
	return channel


def _trigger_rabbitmq(data, rooms, tries=2):
	try:
		channel = get_websocket_channel()
		channel.basic_publish('hightemplar', routing_key='*', body=jsondumps({
			'data': data,
			'rooms': rooms,
		}))
	except (pika.exceptions.StreamLostError, pika.exceptions.AMQPHeartbeatTimeout):
		if tries == 0:
			raise
		get_websocket_channel(force_new=True)
		_trigger_rabbitmq(data, rooms, tries=tries - 1)




def trigger(data, rooms):
	if 'rabbitmq' in getattr(settings, 'HIGH_TEMPLAR', {}):
		_trigger_rabbitmq(data, rooms)
	if getattr(settings, 'HIGH_TEMPLAR_URL', None):
		url = getattr(settings, 'HIGH_TEMPLAR_URL')
		try:
			requests.post('{}/trigger/'.format(url), data=jsondumps({
				'data': data,
				'rooms': rooms,
			}))
		except RequestException:
			pass
