import jsonpickle
from flask import Response, request, render_template, session
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



def init():
    pass