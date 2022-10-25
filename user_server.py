import datetime
import re
import ssl
import time

import jsonpickle
from flask import Response, request, render_template, session

import report_zip
from server_flask import user_bp, not_auth_user, unauthorized
import bot_tg, uuid
import functions as func


@user_bp.route('/', methods=['GET'])
def main_user():
    if not_auth_user():
        return unauthorized()

    if not func.check_user_trusted(session.get('user_id')):
        if func.check_rekrut_form(session.get('user_id')):
            return render_template('form-rekrut-wait.html')
        else:
            return render_template('form-rekrut.html')
    else:
        return render_template('main.html')


@user_bp.route('/rekrut', methods=['POST'])
def save_rekrut():
    if not_auth_user() or func.check_rekrut_form(session.get('user_id')):
        return unauthorized()

    data = request.json

    msg = bot_tg.bot.send_photo(session.get('user_id'), bytes(data['photo']))
    try:
        bot_tg.bot.delete_message(session.get('user_id'), msg.message_id)
    except:
        pass

    func.save_rekrut(session.get('user_id'), data['full_name'], data['birthday'], data['region'], data['qualities'],
                     data['info'], data['reward'], msg.photo[-1].file_id)

    return Response(None, 200)


@user_bp.route('/info', methods=['GET'])
def info_user():
    if not_auth_user():
        return unauthorized()

    return render_template('info.html')


@user_bp.route('/get_missions', methods=['GET'])
def get_missions():
    if not_auth_user():
        return unauthorized()

    return jsonpickle.encode(
        [[i[0], ('✅ ' if (i[2] and i[3]) else
                 ('⚠️ ' if (i[2] and not i[3]) else
                  ('❗️❗️ ' if (not i[2] and i[3]) else '❌ '))) + i[1]] for i in
         func.get_missions_by_user_id(session.get('user_id'))]
    )


@user_bp.route('/mission/<uid>', methods=['GET'])
def mission_info(uid):
    if not_auth_user():
        return unauthorized()

    return render_template('mission_info_user.html')


@user_bp.route('/mission/<uuid>/<method>', methods=['GET'])
def mission_methods(uuid, method):
    if not_auth_user():
        return unauthorized()

    if method == 'geojson':
        return Response(report_zip.get_geojson(uuid, session.get('user_id')), 200, mimetype='application/json',
                        headers={'Access-Control-Allow-Origin': '*',
                                 'Access-Control-Allow-Methods': 'GET',
                                 'Access-Control-Allow-Headers': 'Content-Type,x-requested-with,Access-Control-Allow-Headers'})
    elif method == 'geojson_buildings':
        return Response(report_zip.get_geojson_building(uuid, session.get('user_id')), 200, mimetype='application/json',
                        headers={'Access-Control-Allow-Origin': '*',
                                 'Access-Control-Allow-Methods': 'GET',
                                 'Access-Control-Allow-Headers': 'Content-Type,x-requested-with,Access-Control-Allow-Headers'})
    elif method == 'get_reports_types':
        return Response(jsonpickle.encode(func.get_costs(), unpicklable=False), 200)
    elif method == 'hash':
        return Response('#' +
                        func.get_hash(str(datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                          microsecond=0)) +
                                      str(session.get('user_id'))), 200)
    elif method == 'center_map':
        return Response(report_zip.get_center_map(uuid, session.get('user_id')), 200)


@user_bp.route('/mission/<uid>/add_report', methods=['POST'])
def add_report(uid):
    if not_auth_user():
        return unauthorized()

    json = request.json

    pass_location = func.check_coordinates(uid, json['lat'], json['lon'])
    if pass_location == 0:
        uuid_report = str(uuid.uuid4())
        media_photos_uuid = str(uuid.uuid4())

        photos = []
        videos = []


        for photo in json['photos']:
            msg = bot_tg.bot.send_photo(session.get('user_id'), bytes(photo))

            if not func.check_file_hash(msg.photo[-1].file_unique_id):
                try:
                    bot_tg.bot.delete_message(session.get('user_id'), msg.message_id)
                except:
                    pass
                return Response('3')

            func.add_photo_to_media(media_photos_uuid, msg.photo[-1].file_id, msg.photo[-1].file_unique_id)
            try:
                bot_tg.bot.delete_message(session.get('user_id'), msg.message_id)
            except:
                pass
            time.sleep(0.5)

        msg = bot_tg.bot.send_video(session.get('user_id'), bytes(json['video']))

        if not func.check_file_hash(msg.video.file_unique_id):
            try:
                bot_tg.bot.delete_message(session.get('user_id'), msg.message_id)
            except:
                pass
            return Response('3')

        try:
            bot_tg.bot.delete_message(session.get('user_id'), msg.message_id)
        except:
            pass
        time.sleep(0.5)

        min_distance_to_building = [0, 9999999999999999]
        for key, coords in func.get_coords_buildings(uid, session.get('user_id')).items():
            distance = func.get_length_locations(coords[0], coords[1], json['lat'], json['lon'])
            min_distance_to_building = [key, distance] if distance <= min_distance_to_building[
                1] else min_distance_to_building
        func.save_report_user(uid, session.get('user_id'),
                              (json['lat'], json['lon']),
                              media_photos_uuid, msg.video.file_id,
                              min_distance_to_building[0], json['type_report'])

        return Response('0')
    elif pass_location == 1:
        return Response('1',200)
    elif pass_location == 2:
        for admin_chat_id in func.get_admins():
            bot_tg.bot.send_message(admin_chat_id,
                            f'Система обнаружила, что пользователь {session.get("user_id")} перемещяется слишком быстро.\n'
                            f'Задание: {func.get_full_info_mission(uid)[2]}')

        return Response('2',200)


@user_bp.route('/mission/<uuid>/report', methods=['GET'])
def get_base64_reports(uuid):
    if not_auth_user():
        return unauthorized()

    reports = func.get_reports_by_id(uuid, session.get('user_id'))
    json_report = []
    for _ in range(0, len(reports)):
        json_report.append({})
        json_report[-1]['id'] = _ + 1
        json_report[-1]['date'] = reports[_][3]
        json_report[-1]['building_id'] = reports[_][4]
        json_report[-1]['coords'] = jsonpickle.decode(reports[_][0])
        if reports[_][1].isdigit() or not re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', reports[_][1]) is None:
            reports[_][1] = func.get_photos_by_media_id(reports[_][1])
        json_report[-1]['photos'] = [reports[_][1]] if isinstance(reports[_][1], str) else reports[_][1]
        json_report[-1]['video'] = reports[_][2]

    return jsonpickle.encode(json_report, unpicklable=False)


@user_bp.route('/mission/<uuid>/delete_report', methods=['POST'])
def delete_report(uuid):
    if not_auth_user():
        return unauthorized()

    data = request.json
    func.delete_report(data[0], session.get('user_id'))

    return Response('1', 200)


def init():
    pass
