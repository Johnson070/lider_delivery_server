import datetime
import hashlib
import hmac
import re
import settings
from urllib.parse import unquote


def validate_from_request(data):
    data = data.decode('utf-8')

    time_auth = datetime.datetime.fromtimestamp(0)
    if data.find('&auth_date=') != -1:
        timestamp = re.search(r'&auth_date=([0-9]+)&', data).group(0)
        timestamp = re.search(r'([0-9]+)', timestamp).group(0)
        time_auth = datetime.datetime.fromtimestamp(int(timestamp))

    # TODO: изменить время валидности токена
    hash = re.search(r'&hash=([a-f0-9]+)$', data)
    if hash is not None:
        hash = hash.group(0).replace('&hash=', '')
    else:
        hash = '0'
    return data != '' and (datetime.datetime.now() - time_auth) < datetime.timedelta(seconds=90000000) and validate(
        hash, data, settings.API_KEY)


def validate(hash_str, init_data, token, c_str="WebAppData"):
    init_data = sorted([chunk.split("=")
                        for chunk in unquote(init_data).split("&")
                        if chunk[:len("hash=")] != "hash="],
                       key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    secret_key = hmac.new(c_str.encode(), token.encode(),
                          hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data.encode(),
                          hashlib.sha256)

    return data_check.hexdigest() == hash_str