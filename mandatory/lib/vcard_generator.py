import qrcode
import re

PHONE_TYPES = ["WORK", "HOME", "MAIN", "MOBILE"]

def get_phone_type(line):
    matches = re.search("TYPE=(.+?):", line)

    PHONE_TYPES = ["WORK", "HOME", "MAIN", "MOBILE"]

    for phone_type in PHONE_TYPES:
        if phone_type in matches.group().upper():
            return phone_type
    
    return None

def generate_vcard_string(firstname, lastname, title=None, organisation=None,
                            job_title=None, phone=None, email=None, revision_date=None, birthday=None):
    title = convert_to_str(title)
    organisation = convert_to_str(organisation)
    job_title = convert_to_str(job_title)
    phone = convert_to_str(phone)
    email = convert_to_str(email)
    revision_date = convert_to_str(revision_date)
    birthday = convert_to_str(birthday)

    string = 'BEGIN:VCARD\nVERSION:4.0\n'
    string += f'N:{lastname};{firstname};;{title};\n'
    if organisation != '':
        string += f'ORG:{organisation}\n'
    if job_title != '':
        string += f'TITLE:{job_title}\n'
    
    if phone != '':
        if isinstance(phone, list) or isinstance(phone, tuple):
            for number in phone:
                if isinstance(number, str):
                    string += f"TEL;TYPE=HOME:{number}\n"
                else:
                    string += f"TEL;TYPE={number.get('type', 'HOME')}:{number.get('number', '')}\n"
        elif isinstance(phone, str):
            string += f"TEL;TYPE=HOME:{phone}\n"
        elif isinstance(phone, dict):
            string += f"TEL;TYPE={phone.get('type', 'HOME')}:{phone.get('number')}\n"

    if isinstance(email, list) or isinstance(email, tuple):
        for email_address in email:
            string += f'EMAIL:{email_address}\n'
    elif email != '':
        string += f'EMAIL:{email}\n'
    if revision_date != '':
        string += f'REV:{revision_date}\n'
    string += 'END:VCARD'

    return string

def generate_vcard_qrcode(firstname, lastname, title=None, organisation=None, 
                            job_title=None, phone=None, email=None, revision_date=None, birthday=None):
    vcard_info = generate_vcard_string(firstname, lastname, title, organisation, job_title, phone, email, revision_date, birthday)

    return qrcode.make(vcard_info)

def generate_vcard_qrcode_from_vcard(info):
    return qrcode.make(info)

def convert_to_str(value):
    return '' if value is None else value

def load_data_from_vcard(vcard):
    lines = vcard.splitlines()
    data = {}
    data["phone"] = []

    for line in lines:
        if line.startswith("N:"):
            # name
            linesplit = line.split(":")
            names = linesplit[1].split(";")
            names = list(filter(None, names))
            if len(names) == 1:
                data["firstname"] = names[0]
            elif len(names) >= 2:
                data["lastname"] = names[0]
                data["firstname"] = names[1]
        if line.startswith("ORG:"):
            organization = line.split(":")[1]
            data["organization"] = organization
        if line.startswith("TEL:") or line.startswith("TEL;"):
            phone = {}
            phone_type = get_phone_type(line)

            if phone_type is not None:
                phone["type"] = phone_type

            number = line.split(":")[1]
            phone["number"] = number

            data["phone"].append(phone)
        if line.startswith("TITLE:"):
            data["job_title"] = line.split(":")[1]
        if line.startswith("EMAIL:"):
            data["email"] = line.split(":")[1]
    print(data)
    return data