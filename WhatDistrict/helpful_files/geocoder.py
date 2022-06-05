from requests import get
import sys
from pprint import pprint
from settings import apikey, geocode_server


def get_geocode_object(address):
    """Функция для получения объекта"""
    parameters = {'geocode': address, 'apikey': apikey, 'format': 'json'}
    response = get(geocode_server, params=parameters)
    try:
        return response.json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']
    except Exception:
        if response.status_code == 200:
            print('Адрес задан неправильно')
        else:
            print(f"""Ошибка выполнения запроса
    Http статус: {response.status_code} ({response.reason})""")
            sys.exit(1)


def get_address_pos(address):
    """Функция для получения координат объекта"""
    obj = get_geocode_object(address)
    if obj is not None:
        return list(map(float, obj['Point']['pos'].split()))


def get_kind(pos, kind=None):
    parameters = {'geocode': ','.join(map(str, pos)), 'apikey': apikey,
                  'format': 'json', 'results': 1}
    if kind is not None:
        parameters['kind'] = kind
    response = get(geocode_server, params=parameters)
    if response and kind == 'district':
        components = response.json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocoderMetaData']['Address']['Components']
        return [j for i in components for j in i.values() if 'район' in j][0]