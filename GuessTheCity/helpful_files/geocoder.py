from requests import get
import sys
import os
import pygame
from random import choice
from numpy import arange
from settings import *


def get_geocode_object(address):
    """Функция для получения объекта"""
    parameters = {'geocode': address, 'apikey': apikey, 'format': 'json'}
    response = get(geocode_server, params=parameters)
    try:
        return response.json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']
    except Exception:
        if response.status_code == 200:
            print('Адрес задан неверно')
        else:
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
        dx = abs(float(p1[0]) - float(p2[0]))
        dx = const2 * dx / const1
        dy = abs(float(p1[1]) - float(p2[1]))
        dy = const2 * dy / const1
        return list(map(float, obj['Point']['pos'].split())), f"{dx},{dy}"


def get_random_coords(address):
    obj = get_geocode_object(address)
    if obj is not None:
        envelope = obj['boundedBy']['Envelope']
        p1 = envelope['lowerCorner'].split(' ')
        p2 = envelope['upperCorner'].split(' ')
        x = arange(round(float(p1[0]), 4), round(float(p2[0]), 4), 0.0001)
        y = arange(round(float(p1[1]), 4), round(float(p2[1]), 4), 0.0001)
        return choice(x), choice(y)


def get_image(address, ll=None):
    """Функция для получения изображения объекта"""
    pos, spn = get_address_pos_and_spn(address)
    parameters = {'ll': f'{pos[0]},{pos[1]}' if ll is None else ','.join(
        map(str, ll)),
                  'l': choice(['map', 'sat']), 'spn': spn}
    response = get(static_api_server, params=parameters)
    if response is not None:
        map_file = 'map.png'
        with open(map_file, 'wb') as file:
            file.write(response.content)
        image_to_return = pygame.image.load(map_file)
        os.remove(map_file)
        return image_to_return
