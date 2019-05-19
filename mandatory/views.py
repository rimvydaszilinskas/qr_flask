from flask import send_file, request, render_template, redirect, Response

from mandatory.lib.qr_code_generator import generate_wifi_qrcode, WPA_AUTHENTICATION, generate_link_qrcode, load_wifi_data_from_json
from mandatory.lib.vcard_generator import generate_vcard_qrcode, generate_vcard_string, load_data_from_vcard
from mandatory.lib.location_qr_generator import create_address_qr, create_geo_coordinate_qr, get_geolocation, get_address

import re
from os import remove, path
from io import BytesIO, StringIO
import json

from mandatory import app, ALLOWED_EXTENSIONS

def is_extension_allowed(filename):
    split = filename.split('.')

    extension = split[len(split) - 1]

    if extension in ALLOWED_EXTENSIONS:
        return True

    return False

@app.route('/', methods=['GET'])
def index():
	return redirect('/link')

@app.route('/link', methods=['GET'])
def link_view():
    return render_template('link.html')

@app.route('/link/qr', methods=['POST'])
def link_qr():
    form_data = dict(request.form)
    img_io = BytesIO()

    qr = generate_link_qrcode(link=form_data.get('link'))
    qr.save(img_io, format='PNG', quality=70)
    img_io.seek(0)
    qr.close()

    return send_file(img_io, as_attachment=True, attachment_filename='link_qr.png')

@app.route('/wifi', methods=['GET'])
def wifi_view():
    return render_template('wifi.html')

@app.route('/wifi/qr', methods=['POST'])
def wifi_qr():
    form_data = dict(request.form)
    img_io = BytesIO()

    file_type = form_data.get('file')

    if file_type == 'qr':
        qr = generate_wifi_qrcode(ssid=form_data.get('ssid'), password=form_data.get('ssid'), authentication_type=form_data.get('security'), hidden=form_data.get('hidden') == 'hidden')
        qr.save(img_io, format='PNG', quality=70)
        img_io.seek(0)
        qr.close()

        response = send_file(img_io, as_attachment=True, attachment_filename='qr.png')
        return response
    else:
        wifi_config = {
            'ssid': form_data.get('ssid'),
            'password': form_data.get('password') if form_data.get('security') != 'nopass' else None,
            'security': form_data.get('security'),
            'hidden': form_data.get('hidden') == 'hidden'
        }

        wifi_config_str = json.dumps(wifi_config)

        return Response(wifi_config_str, mimetype='application/json', headers={'Content-Disposition': 'attachement;filename=wifi_config.json'})

@app.route('/wifi/upload', methods=['GET', 'POST'])
def wifi_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('wifi_upload.html')

        json_file = request.files['file']

        if is_extension_allowed(json_file.filename):
            wifi_string = json_file.read().decode('utf-8')
            wifi_data = load_wifi_data_from_json(wifi_string)
            return render_template('wifi.html', wifi=wifi_data)
    else:
        return render_template('wifi_upload.html')

@app.route('/vcard', methods=['GET'])
def vcard_view():
    return render_template('contact.html')

@app.route('/vcard/qr', methods=['POST'])
def vcard_qr():
    form_data = dict(request.form)
    phones = []
    file_type = form_data.get('file')

    for i in form_data:
        if i.startswith('phone'):
            if form_data.get(i) != '':
                identifier = re.findall(r'\d+', i)[0]
                phones.append({'type': form_data.get(f'type{identifier}').upper(), 'number': form_data.get(i)})

    if file_type == 'vcf':
        card_data = generate_vcard_string(firstname=form_data.get('firstname'), lastname=form_data.get('lastname'), organisation=form_data.get('organisation'),
                                        job_title=form_data.get('job_title'), phone=phones, email=form_data.get('email'))
        
        return Response(card_data, mimetype='text/x-vard', headers={'Content-Disposition': 'attachment;filename=vcard.vcf'})

        return 'Error!'
    if file_type == 'qr':
        card = generate_vcard_qrcode(firstname=form_data.get('firstname'), lastname=form_data.get('lastname'), organisation=form_data.get('organisation'),
                                        job_title=form_data.get('job_title'), phone=phones, email=form_data.get('email'))
        img_io = BytesIO()

        card.save(img_io, 'PNG', quality=70)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png', as_attachment=True, attachment_filename='vcard_qr.png')

@app.route('/vcard/vcf', methods=['GET'])
def vcard_upload_view():
    return render_template('vcard_upload.html')

@app.route('/vcard/upload', methods=['POST'])
def vcard_upload():
    if 'file' not in request.files:
        print("no file")
    else:
        file = request.files['file']
        if is_extension_allowed(file.filename):
            vcard_string = file.read().decode('utf-8')
            vcard_data = load_data_from_vcard(vcard_string)
            return render_template('contact.html', contact=vcard_data)
        else:
            print('file not allowed')
    return render_template('vcard_upload.html')

@app.route('/location', methods=['GET'])
def location_view():
    return render_template('location.html')

@app.route('/location/qr', methods=['POST'])
def location_qr():
    form_data = dict(request.form)

    if form_data.get('file') == 'qr':
        if form_data.get('address'):
            qr = create_address_qr(form_data.get('address'))
        else:
            qr = create_geo_coordinate_qr(latitude=form_data.get('latitude'), longitude=form_data.get('longitude'))
        img_io = BytesIO()
        qr.save(img_io, 'PNG', quality=70)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, attachment_filename='location_qr.png')
    else:
        if form_data.get('address', '') != '':
            geolocation = get_geolocation(form_data.get('address'))
            geolocation['address'] = form_data.get('address')

            geolocation_str = json.dumps(geolocation)

            return Response(geolocation_str, mimetype='application/json', headers={'Content-Disposition': 'attachment;filename=location.json'})
        else:
            geolocation = {
                'latitude': form_data.get('latitude', ''),
                'longitude': form_data.get('longitude', '')
            }

            geolocation['address'] = get_address(geolocation['latitude'], geolocation['longitude'])

            geolocation_str = json.dumps(geolocation)

            return Response(geolocation_str, mimetype='application/json', headers={'Content-Disposition': 'attachement;filename=location.json'})

@app.route('/location/json', methods=['GET'])
def upload_location_view():
    return render_template('location_upload.html')

@app.route('/location/upload', methods=['POST'])
def upload_location():
    if 'file' not in request.files:
        return render_template('location_upload.html')
    else:
        location_file = request.files['file']
        if is_extension_allowed(location_file.filename):
            location_file_string = location_file.read().decode('utf-8')

            location = json.loads(location_file_string)

            return render_template('location.html', location=location)
        
        return render_template('location_upload.html')
