from requests import get
import os
import sys
from pprint import pprint
import pygame
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from helpful_files.settings import apikey, geocode_server, static_api_server


def get_geocode_object(address):
    """Функция для получения объекта"""
    parameters = {'geocode': address, 'apikey': apikey, 'format': 'json'}
    response = get(geocode_server, params=parameters)
    try:
        return response.json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']
    except Exception:
        print(f"""Ошибка выполнения запроса
Http статус: {response.status_code} ({response.reason})""")
        sys.exit(1)


def get_address_pos_and_spn(address):
    """Функция для получения координат объекта"""
    obj = get_geocode_object(address)
    if obj is not None:
        envelope = obj['boundedBy']['Envelope']
        p1 = envelope['lowerCorner'].split(' ')
        p2 = envelope['upperCorner'].split(' ')
        dx = abs(float(p1[0]) - float(p2[0])) / 2.0
        dy = abs(float(p1[1]) - float(p2[1])) / 2.0
        return list(map(float, obj['Point']['pos'].split())), f"{dx},{dy}"


def get_image(address, map_type=None):
    """Функция для получения изображения объекта"""
    pos, spn = get_address_pos_and_spn(address)
    parameters = {'ll': f'{pos[0]},{pos[1]}', 'l': 'map', 'spn': spn,
                  'pt': f'{pos[0]},{pos[1]},pm2dgm'}
    if map_type is not None:
        parameters['l'] = map_type
    if spn is not None:
        parameters['spn'] = spn
    response = get(static_api_server, params=parameters)
    if response is not None:
        map_file = 'map.png'
        with open(map_file, 'wb') as file:
            file.write(response.content)
        image_to_return = pygame.image.load(map_file)
        os.remove(map_file)
        return image_to_return
