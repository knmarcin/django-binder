from time import sleep
from threading import Thread
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


def singleton(get_instance):
    instance = None

    def get_singleton():
        nonlocal instance
        if instance is None:
            instance = get_instance()
        return instance

    return get_singleton


@singleton
def get_channel():
    log = 'Calling get_channel...'
    import pika
    connection_credentials = pika.PlainCredentials(
        settings.HIGH_TEMPLAR['rabbitmq']['username'],
        settings.HIGH_TEMPLAR['rabbitmq']['password'],
    )
    connection_parameters = pika.ConnectionParameters(
        settings.HIGH_TEMPLAR['rabbitmq']['host'],
        credentials=connection_credentials,
    )
    state = { 'value': 0 }

    def on_open():
        log += "Opened connection"
        state['value'] = 1

    def on_fail_open():
        log += "Failed to open connection"
        state['value'] = -1

    def on_close():
        log += "Closed connection"
        state['value'] = -2
    
    connection = pika.SelectConnection(
        parameters=connection_parameters,
        on_open_callback=on_open,
        on_open_error_callback=on_fail_open,
        on_close_callback=on_close
    )

    def test_start_loop():
        print("Starting ioloop...")
        connection.ioloop.start()
        print("Finished ioloop")
    
    log += "Starting ioloop thread..."
    Thread(target=test_start_loop).start()
    log += "Started ioloop thread"

    counter = 0

    while state['value'] == 0:
        sleep(0.5)
        counter += 1
        if (counter == 10):
            log += 'final state is ' + str(state['value'])
            raise RuntimeError('Failed to open pika SelectConnection: ' + log)

    if state['value'] != 1:
        raise RuntimeError('Failed to open pika SelectConnection: ' + str(state['value']))
        # TODO Test this approach
    return connection.channel()


def trigger(data, rooms):
    if 'rabbitmq' in getattr(settings, 'HIGH_TEMPLAR', {}):
        channel = get_channel()
        channel.basic_publish('hightemplar', routing_key='*', body=jsondumps({
            'data': data,
            'rooms': rooms,
        }))
    if getattr(settings, 'HIGH_TEMPLAR_URL', None):
        url = getattr(settings, 'HIGH_TEMPLAR_URL')
        try:
            requests.post('{}/trigger/'.format(url), data=jsondumps({
                'data': data,
                'rooms': rooms,
            }))
        except RequestException:
            pass
