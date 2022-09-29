from flask import Flask, session, Response, request, render_template, abort
import hmac
import hashlib, re, datetime
from urllib.parse import unquote

import report_zip
import settings
import functions as func
import jsonpickle
from telebot import types
from bot_tg import bot

app = Flask(__name__)
app.secret_key = settings.cookie_secret_key
prefix = settings.prefix


def not_auth():
    if not 'initdata' in session.keys() or not validate_from_request(session['initdata']):
        return True
    return False


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
    return data != '' and (datetime.datetime.now() - time_auth) < datetime.timedelta(seconds=1000000) and validate(
        hash, data, settings.API_KEY)


def validate(hash_str, init_data, token, c_str="WebAppData"):
    """
    Validates the data received from the Telegram web app, using the
    method documented here:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    hash_str - the has string passed by the webapp
    init_data - the query string passed by the webapp
    token - Telegram bot's token
    c_str - constant string (default = "WebAppData")
    """

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


@app.route(settings.WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@app.route(prefix + '/validate', methods=['GET'])
def validate_query():
    return '0' if not_auth() else '1'


@app.route(prefix + '/validate', methods=['POST'])
def validate_query_save():
    session['initdata'] = request.data
    return '0' if not_auth() else '1'


@app.route(prefix + '/unauthorized')
def unauthorized():
    return Response('<b>401</b><br>Unauthorized<br>Пожалуйста закройте окно и откройте заново!', 401)


@app.route(prefix + '/auth')
def auth():
    return render_template('auth.html')


@app.route(prefix + '/')
def index():
    if not_auth():
        return unauthorized()
    return render_template('index.html')


@app.route(prefix + '/mission/<uuid>', methods=['GET'])
def info_mission(uuid):
    if not_auth():
        return unauthorized()

    try:
        mission = func.get_full_info_mission(uuid)
        count_reports = func.get_count_reports_mission(uuid)
        user = func.get_clerk_by_id(mission[1])[1]

        return render_template('mission_info.html',
                               user=user,
                               name_mission=mission[2],
                               reward=mission[6],
                               count=count_reports,
                               all_count=mission[5],
                               time=mission[4],
                               status='✅ Выполнено' if (mission[7] and mission[8]) else
                               ('⚠️ Ожидает подтверждения' if (mission[7] and not mission[8]) else
                                ('❗️❗️Забраковано' if (not mission[7] and mission[8]) else '❌ Не выполнено')),
                               proof=mission[7] and mission[8],
                               rejected=not mission[7] and mission[8],
                               uuid=mission[0])
    except:
        return unauthorized()


@app.route(prefix + '/get_missions', methods=['GET'])
def get_missions():
    if not_auth():
        return unauthorized()

    all = request.args.get('all')
    missions = func.get_missions(all, True)

    missions = [[i[0], ('✅ ' if (i[2] and i[3]) else
                        ('⚠️ ' if (i[2] and not i[3]) else
                         ('❗️❗️ ' if (not i[2] and i[3]) else '❌ '))) + i[1]] for i in missions]

    return jsonpickle.encode(missions, unpicklable=False)


@app.route(prefix + '/mission/<uuid>/<method>', methods=['GET'])
def manage_mission(uuid, method):
    if not_auth():
        return unauthorized()

    if method == 'to_proof':
        func.proof_mission(uuid)
        return Response(None, 200)
    elif method == 'reject':
        func.reject_mission_by_id(uuid)
        return Response(None, 200)
    elif method == 'retry_rep':
        func.retry_mission_by_id(uuid)
        return Response(None, 200)


# # скачивание файла с сервера телеграмм
# def download_file(file_id):
#     get_file_link = f'https://api.telegram.org/bot{settings.API_KEY}/getFile?file_id={file_id}'
#
#     r = requests.get(get_file_link)
#
#     if r.status_code == 200:
#         file_path = r.json()['result']['file_path']
#         download_file_raw = f'https://api.telegram.org/file/bot{settings.API_KEY}/{file_path}'
#
#         r_data = requests.get(download_file_raw)
#
#         if r_data.status_code == 200:
#             return r_data.content  # base64.b64encode(r_data.text.encode('utf-8'))
#
#     return None


@app.route(prefix + '/get_file', methods=['GET'])
def get_file_by_file_id():
    # if not_auth():
    #     return unauthorized()

    if not 'file_id' in request.args.keys():
        return 'File not found!', 404

    file_id = request.args.get('file_id')

    file = report_zip.get_raw_by_id(file_id)
    if file is not None:
        if file_id.find('DQA') != -1:
            return Response(file, mimetype='video/mp4')
        else:
            return Response(file, mimetype='image/jpeg')

    return Response('File not found!', 200)


@app.route(prefix + '/download/report/<UUID>', methods=['GET'])
def download_report(UUID):
    if not_auth():
        return 0

    file_name = report_zip.get_report(UUID)
    with open(file_name, 'rb') as zip:
        resp = Response(zip.read(), mimetype='application/zip')

    import os
    os.remove(file_name)

    return resp




@app.route(prefix + '/mission/<uuid>/report', methods=['GET'])
def get_base64_reports(uuid):
    if not_auth():
        return unauthorized()

    reports = func.get_reports_by_id(uuid)
    json_report = []
    for _ in range(0, len(reports)):
        json_report.append({})
        json_report[-1]['coords'] = jsonpickle.decode(reports[_][0])
        if reports[_][1].isdigit():
            reports[_][1] = func.get_photos_by_media_id(reports[_][1])
        json_report[-1]['photos'] = [reports[_][1]] if isinstance(reports[_][1], str) else reports[_][1]
        json_report[-1]['video'] = reports[_][2]

    return jsonpickle.encode(json_report, unpicklable=False)


def start_server(debug = False):
    if debug:
        app.run()
    else:
        app.run(debug=True, port=443, host='localhost', ssl_context=('localhost.crt', 'localhost.key'))

#if __name__ == "__main__":
    # app.run()
#    app.run(debug=True, port=443, host='localhost', ssl_context=('localhost.crt', 'localhost.key'))
#else:
#    app.run()
