import re

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
                         ('❗️❗️ ' if (not i[2] and i[3]) else '❌ '))) + i[1]] for i in func.get_missions_by_user_id(session.get('user_id'))]
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
    elif method == 'center_map':
        return Response(report_zip.get_center_map(uuid, session.get('user_id')), 200)


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