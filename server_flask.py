import datetime
import io
import os
import re
import time
from urllib.parse import parse_qs, urlparse

import jsonpickle
from flask import Flask, session, Response, request, render_template, abort, Blueprint
from telebot import types

import bot_tg
import functions as func
import report_zip
import settings
from validate import validate_from_request

os.environ['TZ'] = 'Europe/Moscow' if os.environ.get('TZ') is None else os.environ.get('TZ')
#time.tzset()

project_root = os.path.dirname(os.path.realpath('__file__'))
app = Flask(__name__, static_folder=os.path.join(project_root, 'admin/static'),
            template_folder=os.path.join(project_root, 'admin/templates'))
app.secret_key = settings.cookie_secret_key

moder_bp = Blueprint('moder', __name__,
                     template_folder=os.path.join(project_root, 'moder/templates'),
                     static_folder=os.path.join(project_root, 'moder/static'))
user_bp = Blueprint('user', __name__,
                    template_folder=os.path.join(project_root, 'user/templates'),
                    static_folder=os.path.join(project_root, 'user/static'))
admin_bp = Blueprint('admin', __name__,
                     template_folder=os.path.join(project_root, 'admin/templates'),
                     static_folder=os.path.join(project_root, 'admin/static'))


@app.after_request
def apply_caching(response):
    response.headers["Strict-Transport-Security"] = 'max-age=31536000; includeSubDomains; preload'
    response.headers["Cache-control"] = 'public, max-age:0, must-revalidate'
    return response


def not_auth():
    if not (func.get_user_permission(session.get('user_id')) == settings.permissions[0]) or \
            not func.check_user_in_database(session.get('user_id')) or \
            not validate_from_request(session.get('initdata')):
        return True
    return False


def not_auth_moder():
    if not (func.get_user_permission(session.get('user_id')) == settings.permissions[1]) or \
            not func.check_user_in_database(session.get('user_id')) or \
            not validate_from_request(session.get('initdata')):
        return True
    return False


def not_auth_user():
    if not func.check_user_in_database(session.get('user_id')) or \
            not validate_from_request(session.get('initdata')):
        return True
    return False


#TODO: сделать проверку получения ссылки от отчета и ключа
@admin_bp.before_request
def check_admin():
    if request.method == 'POST' and request.endpoint == 'admin.validate_query_save':
        return
    elif request.method == 'GET' and request.endpoint == 'admin.auth':
        return
    elif request.method == 'GET' and request.endpoint == 'admin.report_get_video_note':
        return
    elif request.method == 'GET' and request.endpoint == 'admin.report_get_photo':
        return
    elif request.method == 'POST' and request.endpoint == 'admin.webhook':
        return
    elif not (func.get_user_permission(session.get('user_id')) in ['admin']) or \
            not func.check_user_in_database(session.get('user_id')):
        return unauthorized()


@moder_bp.before_request
def check_moder():
    if request.method == 'POST' and request.endpoint == 'moder.validate_query_save':
        return
    elif request.method == 'GET' and request.endpoint == 'moder.auth_moder':
        return
    elif not (func.get_user_permission(session.get('user_id')) in ['admin', 'moder']) or \
            not func.check_user_in_database(session.get('user_id')):
        return unauthorized()


@user_bp.before_request
def check_user():
    if request.method == 'POST' and request.endpoint == 'user.validate_query_save':
        return
    elif request.method == 'GET' and request.endpoint == 'user.auth_user':
        return
    elif not (func.get_user_permission(session.get('user_id')) in ['admin', 'moder', 'user']) or \
            not func.check_user_in_database(session.get('user_id')):
        return unauthorized()


@admin_bp.route(settings.WEBHOOK_URL_PATH, methods=['POST', 'GET'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        # bot_tg.bot.load_next_step_handlers(del_file_after_loading=False)

        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot_tg.bot.process_new_updates([update])
        return Response(None, 200)
    else:
        abort(403)


@admin_bp.route('/favicon.ico', methods=['GET'])
def favicon():
    return Response(open('admin/static/favicon.ico', 'rb'), mimetype='image/jpeg')


@moder_bp.route('/validate', methods=['GET'])
@user_bp.route('/validate', methods=['GET'])
@admin_bp.route('/validate', methods=['GET'])
def validate_query():
    if request.blueprint == 'user':
        return unauthorized() if not_auth_user() else Response(None, 200)
    elif request.blueprint == 'moder':
        return unauthorized() if not_auth_moder() else Response(None, 200)
    else:
        return unauthorized() if not_auth() else Response(None, 200)


@moder_bp.route('/validate', methods=['POST'])
@user_bp.route('/validate', methods=['POST'])
@admin_bp.route('/validate', methods=['POST'])
def validate_query_save():
    data_user = parse_qs(request.data.decode('utf-8'))
    if not 'user' in data_user.keys():
        return unauthorized()

    session['user_id'] = jsonpickle.decode(
        data_user['user'][0]
    )['id']
    session['initdata'] = request.data

    if request.blueprint == 'user':
        return unauthorized() if not_auth_user() else Response(None, 200)
    elif request.blueprint == 'moder':
        return unauthorized() if not_auth_moder() else Response(None, 200)
    else:
        return unauthorized() if not_auth() else Response(None, 200)


@admin_bp.route('/unauthorized')
def unauthorized():  #
    return Response(render_template('unauthorized.html'), 401)


@admin_bp.route('/auth')
def auth():
    return render_template('template.html',
                           path='',
                           root=settings.WEBHOOK_URL_BASE)


@user_bp.route('/auth')
def auth_user():
    return render_template('template.html',
                           path='/user',
                           root=settings.WEBHOOK_URL_BASE)


@moder_bp.route('/auth')
def auth_moder():
    return render_template('template.html',
                           path='/moder',
                           root=settings.WEBHOOK_URL_BASE)


@moder_bp.route('/')
@admin_bp.route('/')
def index():
    return render_template('index_moder.html' if request.blueprint == 'moder' else 'index.html')


@admin_bp.route('/mission/<uuid>', methods=['GET'])
@moder_bp.route('/mission/<uuid>', methods=['GET'])
def info_mission(uuid):
    try:
        mission = func.get_full_info_mission(uuid)
        count_reports = func.get_count_reports_mission(uuid)
        user = func.get_clerk_by_id(mission[1])[1]

        return render_template('mission_info_moder.html' if request.blueprint == 'moder' else 'mission_info.html',
                               user=user,
                               name_mission=mission[2],
                               reward=mission[6],
                               count=count_reports,
                               all_count=mission[5],
                               time=mission[4],
                               status='✅ Выполнено' if (mission[7] and mission[8]) else
                               ('⚠️ Ожидает подтверждения' if (mission[7] and not mission[8]) else
                                ('❌️Забраковано' if (not mission[7] and mission[8]) else '🟢 Не выполнено')),
                               proof=mission[7] and mission[8],
                               rejected=not mission[7] and mission[8],
                               uuid=mission[0],
                               user_id=mission[1])
    except:
        return abort(500)


@admin_bp.route('/get_missions', methods=['GET'])
@moder_bp.route('/get_missions', methods=['GET'])
def get_missions():
    all = request.args.get('all')
    missions = func.get_missions(all, True)

    missions = [[i[0], ('✅ ' if (i[2] and i[3]) else
                        ('⚠️ ' if (i[2] and not i[3]) else
                         ('❌️ ' if (not i[2] and i[3]) else '🟢 '))) + i[1]] for i in missions]

    return jsonpickle.encode(missions, unpicklable=False)


@admin_bp.route('/mission/<uuid>/change', methods=['POST'])
def change_mission(uuid):
    json = request.json

    bot_tg.bot.send_message(json['user'], 'Вам было назначено задание')
    func.change_mission(uuid, json['user'], json['name'], json['reward'], json['reports'], json['date'])

    return Response(None, 200)


@admin_bp.route('/mission/<uuid>/<method>', methods=['GET', 'OPTIONS'])
@moder_bp.route('/mission/<uuid>/<method>', methods=['GET', 'OPTIONS'])
def manage_mission(uuid, method):
    if method == 'to_proof':
        func.proof_mission(uuid)
        return Response(None, 200)
    elif method == 'reject':
        func.reject_mission_by_id(uuid)
        mission = func.get_full_info_mission(uuid)

        # bot_tg.bot.send_message(mission[1],
        #                         f'Задание: {mission[2]}!\n'
        #                         'Ваше задание было отбраковано.\n'
        #                         'Свяжитесь с менеджером для уточнения информации.')
        return Response(None, 200)
    elif method == 'retry_rep':
        func.retry_mission_by_id(uuid)
        mission = func.get_full_info_mission(uuid)

        # bot_tg.bot.send_message(mission[1],
        #                         f'Задание: {mission[2]}!\n'
        #                         'Ваше задание было продлено на 1 день.\n'
        #                         'Завершите его в срок.')
        return Response(None, 200)
    elif method == 'delete' and not not_auth():
        func.delete_mission(uuid)
        return Response(None, 200)
    elif method == 'geojson':
        return Response(report_zip.get_geojson(uuid), 200, mimetype='application/json',
                        headers={'Access-Control-Allow-Origin': '*',
                                 'Access-Control-Allow-Methods': 'GET',
                                 'Access-Control-Allow-Headers': 'Content-Type,x-requested-with,Access-Control-Allow-Headers'})
    elif method == 'center_map':
        return Response(report_zip.get_center_map(uuid), 200)
    else:
        return Response(status=404)


@admin_bp.route('/video_note', methods=['GET'])
def report_get_video_note():
    if not 'file_id' in request.args.keys():
        return abort(404)

    file_id = request.args.get('file_id')

    file = func.download_file(file_id)
    if file is not None:
        return Response(file, mimetype='video/mp4')


    return abort(404)


@admin_bp.route('/photo', methods=['GET'])
def report_get_photo():
    if not 'file_id' in request.args.keys():
        return abort(404)

    file_id = request.args.get('file_id')

    file = func.download_file(file_id)
    if file is not None:
        return Response(file, mimetype='image/jpeg')


    return abort(404)


@admin_bp.route('/get_file', methods=['GET'])
@moder_bp.route('/get_file', methods=['GET'])
@user_bp.route('/get_file', methods=['GET'])
def get_file_by_file_id():
    if not 'file_id' in request.args.keys():
        return abort(404)

    file_id = request.args.get('file_id')

    file = func.download_file(file_id)
    if file is not None:
        if file_id.find('AgA') == -1:
            return Response(file, mimetype='video/mp4')
        else:
            return Response(file, mimetype='image/jpeg')

    return abort(404)


@admin_bp.route('/download/report/<UUID>', methods=['GET'])
@moder_bp.route('/download/report/<UUID>', methods=['GET'])
def download_report(UUID):
    file = report_zip.get_report(UUID)
    resp = Response('1', 200)
    bot_tg.bot.send_document(session['user_id'], io.StringIO(file),
                             visible_file_name=f'report_mission_{datetime.datetime.now()}.html')

    return resp


@admin_bp.route('/mission/<uuid>/delete_report', methods=['POST'])
@moder_bp.route('/mission/<uuid>/delete_report', methods=['POST'])
def delete_report(uuid):
    data = request.json
    func.delete_report(data[0], data[1])

    return Response('1', 200)


@admin_bp.route('/mission/<uuid>/delete_building', methods=['POST'])
def delete_building(uuid):
    data = request.json
    func.delete_building(data[0], data[1])

    return Response('1', 200)


@admin_bp.route('/mission/<uuid>/report', methods=['GET'])
@moder_bp.route('/mission/<uuid>/report', methods=['GET'])
def get_base64_reports(uuid):
    reports = func.get_reports_by_id(uuid)
    addrs = None
    if len(reports) > 0:
        route_id = func.get_route_id_by_mission(uuid)
        addrs = func.get_addr_buildings(route_id)

    json_report = []
    for _ in range(0, len(reports)):
        json_report.append({})
        json_report[-1]['id'] = _ + 1
        json_report[-1]['date'] = reports[_][3]
        json_report[-1]['type'] = reports[_][6]
        json_report[-1]['building_id'] = addrs[str(reports[_][4])]
        json_report[-1]['tag'] = \
            func.get_hash(str(datetime.datetime.fromtimestamp(reports[_][3]).replace(hour=0, minute=0, second=0,
                                                                                     microsecond=0)) +
                          str(reports[_][5]))
        json_report[-1]['coords'] = jsonpickle.decode(reports[_][0])
        if reports[_][1].isdigit() or not re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', reports[_][1]) is None:
            reports[_][1] = func.get_photos_by_media_id(reports[_][1])
        json_report[-1]['photos'] = [reports[_][1]] if isinstance(reports[_][1], str) else reports[_][1]
        json_report[-1]['video'] = reports[_][2]

    return jsonpickle.encode(json_report, unpicklable=False)


@admin_bp.route('/routes', methods=['GET'])
def routes():
    return render_template('routes.html')


@admin_bp.route('/routes/<UUID>', methods=['GET'])
def route_view(UUID):
    route = func.get_route(UUID)

    if not len(route):
        return Response(None, 405)

    return render_template('route.html',
                           name=route[1],
                           img=route[4],
                           uuid='https://api-maps.yandex.ru/services/constructor/1.0/js/?um=constructor%3A' +
                                parse_qs(urlparse(route[2]).query)['um'][0].replace('constructor:', '') +
                                '&amp;width=100%25&amp;height=500&amp;lang=ru_RU&amp;scroll=true',
                           can_delete=func.check_can_delete_route(UUID))


@admin_bp.route('/routes/<UUID>/delete', methods=['GET'])
def route_delete(UUID):
    func.delete_route(UUID)

    return Response(None, 200)


@admin_bp.route('/routes/list', methods=['GET'])
def routes_list():
    return Response(jsonpickle.encode(func.get_routes(), unpicklable=False))


@admin_bp.route('/routes/add', methods=['POST'])
def add_route():
    photo = bytes(request.json['photo_bytes'])
    msg_photo = bot_tg.bot.send_photo(session['user_id'], photo)
    photo_file_id = msg_photo.photo[-1].file_id
    bot_tg.bot.delete_message(msg_photo.chat.id, msg_photo.message_id)
    poly = func.parse_geo_json(request.json['geojson'])

    if isinstance(poly, bool) and not poly:
        return Response('-1', 200)
    link_map = request.json['link_map']
    name_route = request.json['name_route']

    import overpy

    api = overpy.Overpass(url='''https://maps.mail.ru/osm/tools/overpass/api/interpreter''')
    points = api.query(f'''
        [out:json];
        nwr[building~'apartments|house|yes'][amenity!~'place_of_worship|doctor|car_wash|courthouse|hospital|clinic'][!shop]["addr:street"](poly:"{poly}");
        out center meta;
    ''')
    id_point = 0

    def parse_addr(node: overpy.Node = None, rel: overpy.Relation = None, way: overpy.Way = None):
        addr = ''
        if node is not None:
            addr += node.tags.get('addr:street', '') + ', '
            addr += node.tags.get('addr:housenumber', '')
        elif rel is not None:
            addr += rel.tags.get('addr:street', '') + ', '
            addr += rel.tags.get('addr:housenumber', '')
        elif way is not None:
            addr += way.tags.get('addr:street', '') + ', '
            addr += way.tags.get('addr:housenumber', '')
        return addr

    coords = [(float(i.center_lat), float(i.center_lon), parse_addr(rel=i)) for i in points.relations]
    coords1 = [(float(i.center_lat), float(i.center_lon), parse_addr(way=i)) for i in points.ways]
    coords2 = [(float(i.lat), float(i.lon), parse_addr(node=i)) for i in points.nodes]

    coords = coords + coords1 + coords2

    addr = {}
    coords_dict = {}
    iter = 0
    for lat, lon, addr_i in coords:
        coords_dict[iter] = (lat, lon)
        addr[iter] = addr_i
        iter += 1

    min_route = func.get_min_route(coords_dict)
    coords_dict = {k: coords_dict[min_route[k]] for k in range(0, len(min_route))}
    addr = {i: addr[min_route[i]] for i in range(0, len(min_route))}

    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', ensure_ascii=False)
    func.add_route([name_route, link_map, jsonpickle.encode(coords_dict), photo_file_id, len(coords),
                    jsonpickle.encode(addr, unpicklable=False)])

    return Response('1', 200)


@admin_bp.route('/users', methods=['GET'])
def users_list():
    return render_template('users.html')


@admin_bp.route('/users/list', methods=['GET'])
@moder_bp.route('/users/list', methods=['GET'])
def get_users_list():
    return jsonpickle.encode(func.get_clerks(), unpicklable=False)


@admin_bp.route('/user/<uid>', methods=['GET'])
def user_profile(uid):
    user = func.get_clerk_by_id(uid)
    return render_template('user_profile.html',
                           user=user[1],
                           balance=user[2],
                           not_pass_balance=user[3])


@admin_bp.route('/user/<uid>/missions', methods=['GET'])
def get_user_missions(uid):
    missions = func.get_missions_by_user_id(uid)
    return jsonpickle.encode(missions, unpicklable=False)


@admin_bp.route('/user/<uid>/<method>', methods=['POST'])
def manage_user(uid, method):
    if method == 'add_mission':
        json = request.json
        mission_id = func.create_new_mission(uid, json['uuid'], json['name'], int(json['days']), json['reward'],
                                             json['reports'])
        bot_tg.bot.send_message(uid,
                                'Вам выдано новое задание!\n'
                                'Старт завтра.')

        return Response(None, 200)
    elif method == 'delete_mission':
        id = request.data.decode('utf-8')
        func.remove_mission_by_id(id)
        return Response(None, 200)
    elif method == 'balance':
        func.change_balance_clerk(uid, float(request.data.decode('utf-8')))
        return Response(None, 200)
    elif method == 'kick':
        kick_with_message = request.data.decode('utf-8')
        func.kick_user(uid)
        if kick_with_message == '1':
            bot_tg.bot.send_message(uid, 'Вы были исключены администратором.\n'
                                     'Спасибо за использование!')
        return Response(None, 200)
    else:
        abort(405)


@admin_bp.route('/location', methods=['GET'])
def get_location():
    return render_template('location.html')


@admin_bp.route('/settings', methods=['GET'])
def settings_page():
    return render_template('settings.html')


@admin_bp.route('/settings/permissions', methods=['GET'])
def get_user_permissions():
    return Response(jsonpickle.encode({i[0]: (i[1], i[2]) for i in func.get_clerks()}, unpicklable=False),
                    mimetype='application/json')


@admin_bp.route('/settings/permissions', methods=['POST'])
def set_user_permissions():
    func.set_user_permission(*request.json)

    return Response('1', 200)


@admin_bp.route('/settings/costs', methods=['GET'])
def get_costs_request():
    return Response(jsonpickle.encode(func.get_costs(), unpicklable=False), mimetype='application/json')


@admin_bp.route('/settings/costs', methods=['POST'])
def set_costs_request():
    func.change_costs(request.json)

    return Response('1', 200)


@admin_bp.route('/settings/download_db/<id>', methods=['GET'])
def download_db(id):
    bot_tg.bot.send_document(id, open(settings.sqlite_file, 'rb'))

    return Response('1', 200)


@admin_bp.route('/settings/create_link/<id>', methods=['GET'])
def create_link(id):
    link, image = func.create_invite_link(id)
    bot_tg.bot.send_photo(id, image,
                          parse_mode='HTML',
                          caption=f'Приглашение активно 6 часов после создания.\n'
                                  f'<a href="{link}">Активировать</a>')

    return Response('1', 200)


@admin_bp.route('/rekruts', methods=['GET'])
def rekruts():
    return render_template('rekruts.html')


@admin_bp.route('/rekruts/get', methods=['GET'])
def rekruts_get():
    return jsonpickle.encode(func.get_rekruts(request.args.get('all')), unpicklable=False)


@admin_bp.route('/rekruts/get_form/<id>', methods=['GET'])
def rekrut_get(id):
    return jsonpickle.encode(func.get_rekrut_info(id), unpicklable=False)


@admin_bp.route('/rekruts/pass', methods=['POST'])
def rekrut_pass():
    func.pass_rekrut(request.json['user_id'])
    try:
        bot_tg.bot.send_message(request.json['user_id'],
                                'Выша анкета соискателя было одобрена!')
    except:
        pass

    return Response('1', 200)


@admin_bp.route('/rekruts/kick', methods=['POST'])
def rekrut_kick():
    func.kick_rekrut(request.json['user_id'])
    try:
        bot_tg.bot.send_message(request.json['user_id'],
                                'Выша анкета соискателя было отклонена!')
    except:
        pass

    return Response('1', 200)


import user_server

if not __name__ == '__main__':
    bot_tg.start_bot()
    user_bp = user_server.init(user_bp, session)

    webhook_info = bot_tg.bot.get_webhook_info()

    if not webhook_info.url == (settings.WEBHOOK_URL_BASE + settings.WEBHOOK_URL_PATH):
        bot_tg.bot.remove_webhook()
        time.sleep(0.1)

        bot_tg.bot.set_webhook(url=settings.WEBHOOK_URL_BASE + settings.WEBHOOK_URL_PATH)

app.register_blueprint(admin_bp, url_prefix='/')
app.register_blueprint(moder_bp, url_prefix='/moder')
app.register_blueprint(user_bp, url_prefix='/user')

application = app
