import wifi_qrcode_generator
import qrcode

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