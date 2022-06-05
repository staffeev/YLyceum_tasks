from requests import get
import sys
import os
from math import radians, cos, acos, sin
import pygame
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


def get_address_pos(address):
    """Функция для получения координат объекта"""
    obj = get_geocode_object(address)
    if obj is not None:
        return list(map(float, obj['Point']['pos'].split()))


def lonlat_distance(p1, p2):
    """Функция, высчитывающая расстояние между двумя точками"""
    p1_lon, p1_lat = map(lambda x: radians(x), p1)
    p2_lon, p2_lat = map(lambda x: radians(x), p2)
    return round(r * acos(sin(p2_lat) * sin(p1_lat) + cos(
        p1_lat) * cos(p2_lat) * cos(p2_lon - p1_lon)), 2)


def get_organization(pos, text='Аптека'):
    """Функция, возвращающая ближайшую организауцию к точке на карте"""
    parameters = {"apikey": apikey_org, "text": text, "lang": "ru_RU",
                  "ll": ','.join(map(str, pos)), "type": "biz"}

    response = get(search_api_server, params=parameters)
    if response:
        return response.json()['features'][0]


def get_organization_data(org):
    """Фуцнкция, возвращающая данные об организации"""
    address = org['properties']['CompanyMetaData']['address']
    name = org['properties']['CompanyMetaData']['name']
    hours = org['properties']['CompanyMetaData']['Hours']['text']
    pos = org['geometry']['coordinates']
    return address, name, hours, pos


def get_image(address, map_type=None, points=None):
    """Функция для получения изображения объекта"""
    pos = get_address_pos(address)
    points_data = ''
    if points is not None:
        points_data = '~' + '~'.join([f'{i[0]},{i[1]},pm2rdm' for i in points])
    parameters = {'ll': f'{pos[0]},{pos[1]}', 'l': 'map',
                  'pt': f'{pos[0]},{pos[1]},pm2dgm' + points_data}
    if map_type is not None:
        parameters['l'] = map_type
    response = get(static_api_server, params=parameters)
    if response is not None:
        map_file = 'map.png'
        with open(map_file, 'wb') as file:
            file.write(response.content)
        image_to_return = pygame.image.load(map_file)
        os.remove(map_file)
        return image_to_return
