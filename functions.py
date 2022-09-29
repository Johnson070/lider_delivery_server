import datetime
import math

import qrcode
import random
import uuid
import sqlite3
import jsonpickle
from io import BytesIO

import settings as sett


def open_db():
    conn = sqlite3.connect(sett.sqlite_file)
    cursor = conn.cursor()
    return conn, cursor


def close_db(conn, cursor):
    cursor.close()
    conn.close()


# парсинг geojson
def parse_geo_json(json):
    points = jsonpickle.decode(json)['features'][0]['geometry']['coordinates']
    points = [(i[0], i[1]) for i in points]

    return points


# создание qr кода на добавление пользователя работает 1 день и только для одного пользователя
def create_invite_link(username):
    uuid_invite_link = str(uuid.uuid4())
    invite_qr = qrcode.make(f'https://t.me/DeliveryLiderBot?start={uuid_invite_link}')
    qr_code_invite_b = BytesIO()
    invite_qr.save(qr_code_invite_b, format='PNG')
    conn, cursor = open_db()

    cursor.execute('''INSERT INTO invites VALUES (?, ?, ?);''',
                   (username, uuid_invite_link,
                    (datetime.datetime.now() + datetime.timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    close_db(conn, cursor)

    return f'https://t.me/DeliveryLiderBot?start={uuid_invite_link}', qr_code_invite_b.getvalue()


# погасить инвайт код
def use_invite_link(code, chat_id, username):
    if check_user_in_database(chat_id, username):
        return True

    conn, cursor = open_db()
    data = cursor.execute(f'SELECT expire FROM invites WHERE code = "{code}"').fetchall()

    if len(data) > 0 and datetime.datetime.strptime(data[0][0], '%Y-%m-%d %H:%M:%S') > datetime.datetime.now():
        cursor.execute(f'DELETE FROM invites WHERE code = ?', (code, ))
        cursor.execute('''INSERT INTO users VALUES (?, ?, ?)''', (chat_id, username, 0.))
        conn.commit()
        close_db(conn, cursor)
        return True
    elif len(data) > 0 and datetime.datetime.strptime(data[0][0], '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
        cursor.execute(f'DELETE FROM invites WHERE code = ?', (code, ))
        conn.commit()

    close_db(conn, cursor)
    return False


def delete_all_links():
    conn, cursor = open_db()
    cursor.execute('''DELETE FROM invites''')
    conn.commit()
    close_db(conn, cursor)


def count_invite_links():
    conn, cursor = open_db()
    count_links = cursor.execute('''SELECT Count() FROM invites''').fetchall()
    close_db(conn, cursor)

    if len(count_links) > 0 and count_links[0][0] is not None:
        count_links = count_links[0][0]
    else:
        return 0

    return count_links


# проверить зарагистрироване ли узверь в системе
def check_user_in_database(chat_id, username):
    conn, cursor = open_db()

    user = cursor.execute('''SELECT username FROM users WHERE id = ? AND username = ?''',
                          (chat_id, username,)).fetchall()

    if len(user) > 0 and user[0][0] == username:
        close_db(conn, cursor)
        return True

    close_db(conn, cursor)
    return False


def add_route(data):
    conn, cursor = open_db()

    cursor.execute('''INSERT INTO routes VALUES (?, ?, ?, ?, ?)''',
                   (str(uuid.uuid4()), data[0], data[1], jsonpickle.encode(data[2]), data[3],))
    conn.commit()
    close_db(conn, cursor)


def get_routes():
    conn, cursor = open_db()
    routes = cursor.execute('''SELECT id,name FROM routes''').fetchall()
    close_db(conn, cursor)

    if len(routes) > 0:
        routes = [(i[0], i[1]) for i in routes]
    else:
        routes = []

    return routes


def get_route(id):
    conn, cursor = open_db()
    route = cursor.execute('''SELECT * FROM routes WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(route) > 0:
        route = route[0]
    else:
        route = ()

    return route


def delete_route(id):
    conn, cursor = open_db()
    cursor.execute('''DELETE FROM routes WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cursor)


def get_clerks():
    conn, cursor = open_db()
    users = cursor.execute('''SELECT id,username FROM users''').fetchall()
    close_db(conn, cursor)

    if len(users) > 0 and users[0][0] is not None:
        users = [(i[0], i[1]) for i in users]
    else:
        users = []
    return users


def get_clerk_by_id(id):
    conn, cursor = open_db()
    user = cursor.execute('''SELECT * FROM users WHERE id = ?''', (id,)).fetchall()
    not_proof = cursor.execute('''SELECT SUM(reward) FROM missions WHERE status = 1 AND proof = 0 AND user = ?''', (id, )).fetchall()
    close_db(conn, cursor)

    if len(user) > 0 and user[0][0] is not None:
        user = list(user[0])
        user.append(not_proof[0][0] if (len(not_proof) > 0 and not_proof[0][0] is not None) else 0)
    else:
        user = []
    return user


def get_mission_by_id(id, not_completed = False):
    conn, cursor = open_db()
    mission = cursor.execute(f'''SELECT comment FROM missions WHERE id = ?
                            {' AND status = "0"' if not_completed else ''}''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(mission) > 0 and mission[0][0] is not None:
        mission = mission[0][0]
    else:
        mission = None
    return mission


def get_full_info_mission(id):
    conn, cursor = open_db()
    mission = cursor.execute('''SELECT * FROM missions WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(mission) > 0 and mission[0][0] is not None:
        mission = list(mission[0])
    else:
        mission = None
    return mission


def get_missions_by_user_id(user_id):
    conn, cursor = open_db()
    missions = cursor.execute('''SELECT id,comment FROM missions WHERE user = ? AND proof = "0"''', (user_id,)).fetchall()
    close_db(conn, cursor)

    data_missions = []
    if len(missions) > 0 and missions[0][0] is not None:
        data_missions = [(i[0], i[1]) for i in missions]

    return data_missions


def create_new_mission(user_id, id_route, comment, expire_days, reward, count_reports):
    conn, cursor = open_db()
    current_time = datetime.datetime.now()
    mission_id = str(uuid.uuid4())
    cursor.execute('''INSERT INTO missions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (mission_id, user_id, comment, id_route,
                    (datetime.datetime(year=current_time.year, month=current_time.month,
                                       day=current_time.day,
                                       hour=23, minute=59, second=59) +
                     datetime.timedelta(days=expire_days)).strftime('%Y-%m-%d %H:%M:%S'),
                    count_reports, reward, False, False))
    conn.commit()
    close_db(conn, cursor)

    return mission_id


def remove_mission_by_id(id):
    conn, cursor = open_db()
    cursor.execute('''DELETE FROM missions WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cursor)


def get_count_reports_mission(id):
    conn, cursor = open_db()
    count = cursor.execute('''SELECT COUNT(*) FROM reports WHERE mission_id = ?''',
                           (id,)).fetchall()
    close_db(conn, cursor)

    if len(count) > 0 and count[0][0] is not None:
        count = count[0][0]

    return count


def get_missions(all_by_desc=False, web=False):
    conn, cursor = open_db()
    missions = None

    if web:
        if all_by_desc:
            missions = cursor.execute(
                '''SELECT id,comment,status,proof FROM missions ORDER BY date_expire DESC''').fetchall()
        else:
            missions = cursor.execute(
                '''SELECT id,comment,status,proof FROM missions WHERE status = 1 AND proof = 0''').fetchall()
        close_db(conn, cursor)

        if len(missions) > 0 and missions[0][0] is not None:
            missions = [[i[0], i[1], i[2], i[3]] for i in missions]
        else:
            return []
    else:
        if all_by_desc:
            missions = cursor.execute('''SELECT id,comment FROM missions ORDER BY date_expire DESC''').fetchall()
        else:
            missions = cursor.execute('''SELECT id,comment FROM missions WHERE status = 1 AND proof = 0''').fetchall()
        close_db(conn, cursor)

        if len(missions) > 0 and missions[0][0] is not None:
            missions = [[i[0], i[1]] for i in missions]
        else:
            return []

    return missions


def get_location_start_for_mission(id):
    conn, cursor = open_db()
    location = cursor.execute('''SELECT coords FROM routes WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(location) > 0 and location[0][0] is not None:
        location = location[0][0]
        location = jsonpickle.decode(location)[0]
        return location

    return None


# def set_channel_photo_sklad(id_channel):
#     conn, cursor = open_db()
#     cursor.execute('DELETE FROM channel_photo')
#     cursor.execute(f'INSERT INTO channel_photo VALUES ("{id_channel}")')
#     conn.commit()
#     close_db(conn, cursor)
#
#
# def get_channel_photo_sklad():
#     conn, cursor = open_db()
#     row = cursor.execute('SELECT id FROM channel_photo').fetchall()
#     close_db(conn, cursor)
#
#     return int(row[0][0]) if len(row) > 0 else None


def save_report_user(id, user_id, location, photo_id, video_id):
    conn, cursor = open_db()
    location = jsonpickle.encode(location)
    cursor.execute('''INSERT INTO reports VALUES (?, ?, ?, ?, ?)''', (id, user_id, location, photo_id, video_id,))
    conn.commit()


def complete_mission(id):
    conn, cur = open_db()
    cur.execute('''UPDATE missions SET status = "1" WHERE id = ?''', (id, ))
    conn.commit()
    close_db(conn, cur)


def add_photo_to_media(msg_id, file_id):
    conn, cur = open_db()
    cur.execute('''INSERT INTO media VALUES (?, ?)''', (msg_id, file_id,))
    conn.commit()
    close_db(conn, cur)


def get_photos_by_media_id(media_group_id):
    conn, cur = open_db()
    ids = cur.execute('''SELECT file_id FROM media WHERE photo_id = ?''', (media_group_id,)).fetchall()
    close_db(conn, cur)

    if len(ids) > 0 and ids[0][0] is not None:
        ids = [i[0] for i in ids]
    else:
        return []

    return ids


def change_balance_clerk(id, balance):
    conn, cur = open_db()
    cur.execute('''UPDATE users SET earned = ? WHERE id = ?''', (balance,id,))
    conn.commit()
    close_db(conn, cur)


def kick_user(id):
    conn, cur = open_db()
    cur.execute('''DELETE FROM users WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def proof_mission(id):
    conn, cur = open_db()
    user, reward = cur.execute('''SELECT user,reward FROM missions WHERE id = ?''', (id, )).fetchall()[0]
    cur.execute('''UPDATE users SET earned = earned + ? WHERE id = ?''', (reward, user, ))
    cur.execute('''UPDATE missions SET proof = 1, status = 1 WHERE id = ?''', (id, ))
    conn.commit()
    close_db(conn, cur)


def retry_mission_by_id(id):
    conn, cur = open_db()
    cur.execute('''UPDATE missions SET date_expire = 
                        IIF(date_expire >= DATETIME("now"), DATETIME(date_expire,"+1 day"), DATETIME("now","start of day","+3 days","-1 second")) 
                        WHERE id = ?''', (id, ))
    cur.execute('''UPDATE missions SET status = 0, proof = 0 WHERE id = ?''', (id, ))
    conn.commit()
    close_db(conn, cur)


def reject_mission_by_id(id):
    conn, cur = open_db()
    mission = cur.execute('''SELECT status, proof, reward, user FROM missions WHERE id = ?''', (id, )).fetchall()[0]
    cur.execute('''UPDATE users SET earned = earned - IIF(? = 1 AND ? = 1, ?, 0) WHERE id = ?''', *(mission,))
    cur.execute('''UPDATE missions SET status = 0,proof = 1 WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def get_reports_by_id(id):
    conn, cur = open_db()
    reports = cur.execute('''SELECT location,photo_id,video_id FROM reports WHERE mission_id = ?''', (id,)).fetchall()
    close_db(conn, cur)

    if len(reports) > 0 and reports[0][0] is not None:
        ids = [[i[0], i[1], i[2]] for i in reports]
    else:
        return []

    return ids


def check_coordinates(id_mission, lat, lon):
    conn, cur = open_db()
    id_route = cur.execute('''SELECT id_route FROM missions WHERE id = ?''', (id_mission,)).fetchall()[0][0]

    coords = cur.execute('''SELECT coords FROM routes WHERE id = ?''', (id_route,)).fetchall()
    close_db(conn, cur)
    coords = jsonpickle.decode(coords[0][0])

    for pos in coords:
        # print(get_length_locations(lat, lon, pos[0], pos[1]), lat, lon, pos[0], pos[1] )
        if get_length_locations(lat, lon, pos[0], pos[1]) <= sett.allow_radius:
            return True

    return False


def get_length_locations(lat1, lon1, lat2, lon2):
    def degrees_to_rads(deg):
        return (deg * math.pi) / 180.0
    lat1 = degrees_to_rads(lat1)
    lat2 = degrees_to_rads(lat2)
    lon1 = degrees_to_rads(lon1)
    lon2 = degrees_to_rads(lon2)
    return 2 * 6371 * math.asin(math.sqrt(
        math.pow(math.sin(((lat2-lat1)/2.0)), 2.0) +
        math.cos(lat1) * math.cos(lat2) *
        math.pow(math.sin(((lon2-lon1)/2.0)), 2.0)
    ))


# Генерация псевдослучайных чисел задание зерна
rd = random.Random()
rd.seed(datetime.datetime.now().microsecond)
uuid.UUID(int=rd.getrandbits(128))
