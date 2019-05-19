import wifi_qrcode_generator
import qrcode
import json

WPA_AUTHENTICATION = 'WPA'
WEP_AUTHENTICATION = 'WEP'
NO_AUTHENTICATION = 'nopass'

def generate_wifi_qrcode(ssid, password=None, authentication_type=None, hidden=False):
    if authentication_type is None or authentication_type == 'nopass':
        authentication_type = 'nopass'
        password = None

    return wifi_qrcode_generator.wifi_qrcode(ssid, hidden, authentication_type, password)

def generate_link_qrcode(link='https://rimvydas.site'):
    if not link.startswith('http://') or not link.startswith('https://'):
        link = 'http://' + link
    
    return qrcode.make(data=link)

def load_wifi_data_from_json(wifi_string):
    wifi_config = json.loads(wifi_string)

    wifi_config['password'] = None if wifi_config['security'] == 'nopass' else wifi_config['password']

    return wifi_config