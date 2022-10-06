from flask import Flask, session, Response, request, render_template, abort
import hmac
import hashlib, re, datetime
from urllib.parse import unquote, parse_qs, urlparse
import os

import report_zip
import settings
import functions as func
import jsonpickle
# from telebot import types
# import bot_tg

app = Flask(__name__)
app.secret_key = settings.cookie_secret_key
application = app


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


# @app.route(settings.WEBHOOK_URL_PATH, methods=['POST','GET'])
# def webhook():
#     if request.headers.get('content-type') == 'application/json':
#         json_string = request.get_data().decode('utf-8')
#         update = types.Update.de_json(json_string)
#         bot_tg.bot.process_new_updates([update])
#         return ''
#     else:
#         abort(403)


@app.route('/validate', methods=['GET'])
def validate_query():
    return '0' if not_auth() else '1'


@app.route('/validate', methods=['POST'])
def validate_query_save():
    data_user = parse_qs(request.data.decode('utf-8'))

    if not 'user' in data_user.keys():
        return '0'

    session['user_id'] = jsonpickle.decode(
        data_user['user'][0]
    )['id']
    session['initdata'] = request.data
    return '0' if not_auth() else '1'


@app.route('/unauthorized')
def unauthorized():
    return Response('<b>401</b><br>Unauthorized<br>Пожалуйста закройте окно и откройте заново!', 401)


@app.route('/auth')
def auth():
    # return "", 200

    return render_template('auth.html')


@app.route('/')
def index():
    if not_auth():
        return unauthorized()

    return render_template('index.html')


@app.route('/mission/<uuid>', methods=['GET'])
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


@app.route('/get_missions', methods=['GET'])
def get_missions():
    if not_auth():
        return unauthorized()

    all = request.args.get('all')
    missions = func.get_missions(all, True)

    missions = [[i[0], ('✅ ' if (i[2] and i[3]) else
                        ('⚠️ ' if (i[2] and not i[3]) else
                         ('❗️❗️ ' if (not i[2] and i[3]) else '❌ '))) + i[1]] for i in missions]

    return jsonpickle.encode(missions, unpicklable=False)


@app.route('/mission/<uuid>/<method>', methods=['GET'])
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


@app.route('/get_file', methods=['GET'])
def get_file_by_file_id():
    if not_auth():
        return unauthorized()

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


@app.route('/download/report/<UUID>', methods=['GET'])
def download_report(UUID):
    if not_auth():
        return 0

    file_name = report_zip.get_report(UUID)
    with open(file_name, 'rb') as zip:
        file = zip.read()
        resp = Response(file, mimetype='application/zip')
        bot.send_document(session['user_id'], file,
                          visible_file_name=f'report_mission_{datetime.datetime.now()}.zip')

    os.remove(file_name)

    return resp


@app.route('/mission/<uuid>/report', methods=['GET'])
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


@app.route('/routes', methods=['GET'])
def routes():
    if not_auth():
        return unauthorized()

    return render_template('routes.html')


@app.route('/routes/<UUID>', methods=['GET'])
def route_view(UUID):
    if not_auth():
        return unauthorized()

    route = func.get_route(UUID)

    return render_template('route.html',
                           name=route[1],
                           img=route[4],
                           uuid='https://api-maps.yandex.ru/services/constructor/1.0/js/?um=constructor%3A' +
                                parse_qs(urlparse(route[2]).query)['um'][0].replace('constructor:','') +
                                '&amp;width=100%25&amp;height=500&amp;lang=ru_RU&amp;scroll=true',
                           can_delete=func.check_can_delete_route(UUID))


@app.route('/routes/<UUID>/delete', methods=['GET'])
def route_delete(UUID):
    if not_auth():
        return unauthorized()

    func.delete_route(UUID)

    return Response(1, 200)


@app.route('/routes/list', methods=['GET'])
def routes_list():
    if not_auth():
        return unauthorized()

    return Response(jsonpickle.encode(func.get_routes(), unpicklable=False))


@app.route('/routes/add', methods=['POST'])
def add_route():
    if not_auth():
        return unauthorized()
    photo = bytes(request.json['photo_bytes'])
    msg_photo = bot.send_photo(session['user_id'], photo)
    photo_file_id = msg_photo.photo[-1].file_id
    bot.delete_message(msg_photo.chat.id, msg_photo.message_id)
    geojson = func.parse_geo_json(request.json['geojson'])
    if isinstance(geojson, bool) and not geojson:
        return Response('-1', 200)
    link_map = request.json['link_map']
    name_route = request.json['name_route']

    func.add_route([name_route, link_map, geojson, photo_file_id])

    return Response('1',200)


@app.route('/users', methods=['GET'])
def users_list():
    if not_auth():
        return unauthorized()

    return render_template('users.html')


@app.route('/users/list', methods=['GET'])
def get_users_list():
    if not_auth():
        return unauthorized()

    return jsonpickle.encode(func.get_clerks(), unpicklable=False)


@app.route('/user/<uid>', methods=['GET'])
def user_profile(uid):
    if not_auth():
        return unauthorized()

    user = func.get_clerk_by_id(uid)
    return render_template('user_profile.html',
                           user=user[1],
                           balance=user[2],
                           not_pass_balance=user[3])


@app.route('/user/<uid>/missions', methods=['GET'])
def get_user_missions(uid):
    if not_auth():
        return unauthorized()

    missions = func.get_missions_by_user_id(uid)
    return jsonpickle.encode(missions, unpicklable=False)


@app.route('/user/<uid>/<method>', methods=['POST'])
def manage_user(uid, method):
    if not_auth():
        return unauthorized()

    if method == 'add_mission':
        json = request.json
        func.create_new_mission(uid, json['uuid'], json['name'], int(json['days']), json['reward'], json['reports'])
        return Response(None, 200)
    elif method == 'delete_mission':
        id = request.data.decode('utf-8')
        func.remove_mission_by_id(id)
        return Response(None, 200)
    elif method == 'balance':
        func.change_balance_clerk(uid, float(request.data.decode('utf-8')))
        return Response(None, 200)
    elif method == 'kick':
        func.kick_user(uid)
        return Response(None, 200)
    else:
        Response(None, 401)


@app.route('/location', methods=['GET'])
def get_location():
    return render_template('location.html')


def start_server(debug = False):
    if debug:
        app.run()
    else:
        app.run(debug=True, port=443, host='192.168.3.198', ssl_context=('localhost.crt', 'localhost.key'))

# if __name__ == "__main__":
#    app.run(debug=True, port=443, host='localhost', ssl_context=('localhost.crt', 'localhost.key'))
# else:
#    app.run()
