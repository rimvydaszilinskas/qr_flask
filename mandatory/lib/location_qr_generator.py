import qrcode
import requests
import json

import os
from mandatory import app

def create_geo_coordinate_qr(latitude, longitude):
    location = f'geo:{latitude},{longitude}'

    return qrcode.make(location)

def create_address_qr(address):
    coordinates = get_geolocation(address)

    if coordinates is not None:
        return create_geo_coordinate_qr(latitude=coordinates.get('latitude'), longitude=coordinates.get('longitude'))
    return None

def get_geolocation(address):
    with open(os.path.join(app.root_path, 'config', 'config.json')) as config_file:
        coordinate = {}

        config = json.load(config_file)

        google_api_config = config.get('google').get('maps').get('api')
        geocoding_config = google_api_config.get('geocoding')

        api_key = google_api_config.get('key')
        geocoding_url = geocoding_config.get('url')

        url = geocoding_url.format(**locals())

        response = requests.get(url)

        address = json.loads(response.text)

        if len(address.get('results')) == 0:
            return None
        
        coordinate['latitude'] = address['results'][0]['geometry']['location']['lat']
        coordinate['longitude'] = address['results'][0]['geometry']['location']['lng']

        return coordinate

    return None

def get_address(latitude, longitude):
    with open(os.path.join(app.root_path, 'config', 'config.json')) as config_file:
        config = json.load(config_file)

        google_api_config = config.get('google').get('maps').get('api')
        geocoding_config = google_api_config.get('reverse_geocoding')

        api_key = google_api_config.get('key')
        geocoding_url = geocoding_config.get('url')

        url = geocoding_url.format(**locals())

        response = requests.get(url)

        location = json.loads(response.text)

        if len(location.get('results')) == 0:
            return None
        
        address = location['results'][0]['formatted_address']

        return address

    return None