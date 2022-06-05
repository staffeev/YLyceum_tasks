import requests

apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
static_url = 'https://static-maps.yandex.ru/1.x/?'
geocode_server = 'https://geocode-maps.yandex.ru/1.x?'
const1 = 1.33441
const2 = 0.05


def get_geocode_object(address):
    """Функция для получения объекта"""
    parameters = {'geocode': address, 'apikey': apikey, 'format': 'json'}
    response = requests.get(geocode_server, params=parameters)
    try:
        return response.json()['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']
    except Exception:
        return


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
