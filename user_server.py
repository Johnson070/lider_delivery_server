import datetime
import re
import time

import flask
import jsonpickle
from flask import Response, request, render_template, abort

import bot_tg
import functions as func
import markups
import report_zip
import uuid
import threading

import settings
import user_handlers
from validate import validate_from_request


def init(user_bp: flask.Blueprint, session: flask.session):
    def unauthorized():
        return Response(render_template('unauthorized.html'), 401)

    def delete_message(message_id, user_id):
        time.sleep(5*60)
        try:
            bot_tg.bot.delete_message(user_id, message_id)
        except:
            pass

        photo_id = func.get_photo_id_request_report(user_id)
        func.delete_media_by_group_id(photo_id)
        func.delete_request_report(user_id)

    @user_bp.route('/', methods=['GET'])
    def main_user():
        if not func.check_user_trusted(session.get('user_id')):
            if func.check_rekrut_form(session.get('user_id')):
                return render_template('form-rekrut-wait.html')
            else:
                return render_template('form-rekrut.html')
        else:
            return render_template('main.html')

    @user_bp.route('/rekrut', methods=['POST'])
    def save_rekrut():
        if func.check_rekrut_form(session.get('user_id')):
            return unauthorized()

        data = request.json

        msg = bot_tg.bot.send_photo(session.get('user_id'), bytes(data['photo']))
        try:
            bot_tg.bot.delete_message(session.get('user_id'), msg.message_id)
        except:
            pass

        func.save_rekrut(session.get('user_id'), data['full_name'], data['birthday'], data['region'], data['qualities'],
                         data['info'], data['reward'], msg.photo[-1].file_id, data['time_work'], data['national'])

        return Response(None, 200)

    @user_bp.route('/info', methods=['GET'])
    def info_user():
        return render_template('info.html',
                               name=func.get_clerk_by_id(session.get('user_id'))[1],
                               balance='100')

    @user_bp.route('/get_missions', methods=['GET'])
    def get_missions():
        return jsonpickle.encode(
            [[i[0], ('✅ ' if (i[2] and i[3]) else
                     ('⚠️ ' if (i[2] and not i[3]) else
                      ('❌️ ' if (not i[2] and i[3]) else '🟢 '))) + i[1]] for i in
             func.get_missions_by_user_id(session.get('user_id'))]
        )

    @user_bp.route('/mission/<uid>', methods=['GET'])
    def mission_info(uid):
        if not func.check_mission_exists(uid, session.get('user_id')):
            return abort(404)

        mission = func.get_full_info_mission(uid, session.get('user_id'))
        buildings = func.get_route_buildings(mission[3])

        expired = True if datetime.datetime.strptime(mission[4],
                                                     '%Y-%m-%d %H:%M:%S') < datetime.datetime.now() else False
        expired = True if mission[7] == 1 else expired
        end = mission[7] and not mission[8]

        time_todo = datetime.datetime.strptime(mission[4], "%Y-%m-%d %H:%M:%S")
        if time_todo < datetime.datetime.now():
            time_todo = datetime.timedelta(0, 0, 0, 0, 0, 0, 0)
        else:
            time_todo = time_todo - datetime.datetime.now()

        return render_template('mission_info_user.html',
                               name=mission[2],
                               reward=mission[6],
                               time=f'{time_todo.days} дн {time_todo.seconds // 60 // 60 % 60} час {time_todo.seconds // 60 % 60} минут',
                               buildings=buildings,
                               end=end,
                               expired=expired,
                               status='✅ Выполнено' if (mission[7] and mission[8]) else
                               ('⚠️ Ожидает подтверждения' if (mission[7] and not mission[8]) else
                                ('❌️Забраковано' if (not mission[7] and mission[8]) else '🟢 Не выполнено')))

    @user_bp.route('/mission/<uuid>/<method>', methods=['GET'])
    def mission_methods(uuid, method):
        if not func.check_mission_exists(uuid, session.get('user_id')):
            return abort(404)

        if method == 'geojson':
            return Response(report_zip.get_geojson(uuid, session.get('user_id')), 200, mimetype='application/json',
                            headers={'Access-Control-Allow-Origin': '*',
                                     'Access-Control-Allow-Methods': 'GET',
                                     'Access-Control-Allow-Headers': 'Content-Type,x-requested-with,Access-Control-Allow-Headers'})
        elif method == 'geojson_buildings':
            return Response(report_zip.get_geojson_building(uuid, session.get('user_id')), 200,
                            mimetype='application/json',
                            headers={'Access-Control-Allow-Origin': '*',
                                     'Access-Control-Allow-Methods': 'GET',
                                     'Access-Control-Allow-Headers': 'Content-Type,x-requested-with,Access-Control-Allow-Headers'})
        elif method == 'get_reports_types':
            return Response(jsonpickle.encode(func.get_costs(), unpicklable=False), 200)
        elif method == 'hash':
            return Response(func.get_hash(str(datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                              microsecond=0)) +
                                          str(session.get('user_id'))), 200)
        elif method == 'pass':
            func.complete_mission(uuid, session.get('user_id'))
            return Response(None, 200)
        elif method == 'center_map':
            return Response(report_zip.get_center_map(uuid, session.get('user_id')), 200)

    @user_bp.route('/mission/<uid>/add_report', methods=['POST'])
    def add_report(uid):
        if not func.check_mission_exists(uid, session.get('user_id')):
            return abort(404)

        json = request.json

        mission = func.get_full_info_mission(uid, session.get('user_id'))
        expired = True if datetime.datetime.strptime(mission[4],
                                                     '%Y-%m-%d %H:%M:%S') < datetime.datetime.now() else False
        expired = True if mission[7] == 1 else expired
        end = mission[7] and not mission[8]

        if expired or end:
            return Response('-1', 200)
        elif func.get_request_report(session.get('user_id')):
            msg_id = func.get_request_report(session.get('user_id'))[6]
            try:
                bot_tg.bot.delete_message(session.get('user_id'), msg_id)
            except:
                pass

            photo_id = func.get_photo_id_request_report(session.get('user_id'))
            func.delete_media_by_group_id(photo_id)
            func.delete_request_report(session.get('user_id'))

        pass_location = func.check_coordinates(uid, json['lat'], json['lon'])
        if pass_location == 0:
            min_distance_to_building = [0, 9999999999999999]
            for key, coords in func.get_coords_buildings(uid, session.get('user_id')).items():
                distance = func.get_length_locations(coords[0], coords[1], json['lat'], json['lon'])
                min_distance_to_building = [key, distance] if distance <= min_distance_to_building[1] \
                    else min_distance_to_building

            msg = bot_tg.bot.send_message(session.get('user_id'),
                                          'Сначала отправьте фотографии СО СЖАТИЕМ, ПОТОМ кружочек.\n'
                                          'На видео и фото должен отчетливо виден тэг.\n'
                                          'У вас есть 5 минут на отправку отчета.',
                                          reply_markup=markups.end_send_media('interrupt_report'))

            threading.Thread(target=delete_message, args=(msg.message_id, session.get('user_id'))).start()

            func.add_request_report(session.get('user_id'), uid, jsonpickle.encode((json['lat'], json['lon'])),
                                    min_distance_to_building[0], json['type_report'], msg.message_id)

            return Response('0')
        elif pass_location == 1:
            return Response('1', 200)
        elif pass_location == 2:
            for admin_chat_id in func.get_admins():
                bot_tg.bot.send_message(admin_chat_id,
                                        f'Система обнаружила, что пользователь {session.get("user_id")} перемещяется слишком быстро.\n'
                                        f'Задание: {func.get_full_info_mission(uid)[2]}')

            return Response('2', 200)

    @user_bp.route('/mission/<uuid>/report', methods=['GET'])
    def get_base64_reports(uuid):
        if not func.check_mission_exists(uuid, session.get('user_id')):
            return abort(404)

        reports = func.get_reports_by_id(uuid, session.get('user_id'))
        addrs = None
        if len(reports) > 0:
            addrs = func.get_addr_buildings(uuid, session.get('user_id'))

        json_report = []
        for _ in range(0, len(reports)):
            json_report.append({})
            json_report[-1]['id'] = _ + 1
            json_report[-1]['date'] = reports[_][3]
            json_report[-1]['building_id'] = addrs[str(reports[_][4])]
            json_report[-1]['tag'] = \
                func.get_hash(str(datetime.datetime.fromtimestamp(reports[_][3]).replace(hour=0, minute=0, second=0,
                                                                                         microsecond=0)) +
                              str(session.get('user_id')))
            json_report[-1]['coords'] = jsonpickle.decode(reports[_][0])
            if reports[_][1].isdigit() or not re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', reports[_][1]) is None:
                reports[_][1] = func.get_photos_by_media_id(reports[_][1])
            json_report[-1]['photos'] = [reports[_][1]] if isinstance(reports[_][1], str) else reports[_][1]
            json_report[-1]['video'] = reports[_][2]

        return jsonpickle.encode(json_report, unpicklable=False)

    @user_bp.route('/mission/<uuid>/delete_report', methods=['POST'])
    def delete_report(uuid):
        if not func.check_mission_exists(uuid, session.get('user_id')):
            return abort(405)

        data = request.json
        func.delete_report(data[0], session.get('user_id'))

        return Response('1', 200)

    return user_bp
