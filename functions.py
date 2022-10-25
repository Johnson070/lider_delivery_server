import datetime
import hashlib
import math
import re

import qrcode
import random
import uuid
import sqlite3
import jsonpickle
from io import BytesIO

import requests

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
    try:
        points = jsonpickle.decode(json)

        if points['features'][0]['geometry']['type'] == 'Polygon':

            poly = ''
            for i in points['features'][0]['geometry']['coordinates'][0]:
                poly += f'{i[1]} {i[0]} '

            return poly[0:-2]
        else:
            return False
    except:
        return False


def get_hash(s, char_length=8):
    """Geneate hexadecimal string with given length from a string
    >>> short_str("hello world", 8)
    '309ecc48'
    """

    if char_length > 128:
        raise ValueError("char_length {} exceeds 128".format(char_length))
    hash_object = hashlib.sha512(s.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex[0:char_length].upper()


# создание qr кода на добавление пользователя работает 1 день и только для одного пользователя
def create_invite_link(username, permission):
    uuid_invite_link = str(uuid.uuid4())
    invite_qr = qrcode.make(f'https://t.me/DeliveryLiderBot?start={uuid_invite_link}')
    qr_code_invite_b = BytesIO()
    invite_qr.save(qr_code_invite_b, format='PNG')
    conn, cursor = open_db()

    cursor.execute('''INSERT INTO invites VALUES (?, ?, ?, ?);''',
                   (username, uuid_invite_link,
                    (datetime.datetime.now() + datetime.timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'), permission,))
    conn.commit()
    close_db(conn, cursor)

    return f'https://t.me/DeliveryLiderBot?start={uuid_invite_link}', qr_code_invite_b.getvalue()


# погасить инвайт код
def use_invite_link(code, chat_id, username):
    if check_user_in_database(chat_id, username):
        return True

    conn, cursor = open_db()
    data = cursor.execute(f'SELECT expire, permission FROM invites WHERE code = "{code}"').fetchall()

    if len(data) > 0 and datetime.datetime.strptime(data[0][0], '%Y-%m-%d %H:%M:%S') > datetime.datetime.now():
        cursor.execute(f'DELETE FROM invites WHERE code = ?', (code,))
        cursor.execute('''INSERT INTO users VALUES (?, ?, ?, ?, ?)''', (chat_id, username, 0., data[0][1], 1 if data[0][1] != 'user' else 0))
        conn.commit()
        close_db(conn, cursor)
        return True
    elif len(data) > 0 and datetime.datetime.strptime(data[0][0], '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
        cursor.execute(f'DELETE FROM invites WHERE code = ?', (code,))
        conn.commit()

    close_db(conn, cursor)
    return False


def get_user_permission(id):
    conn, cursor = open_db()
    permission = cursor.execute('''SELECT permissions FROM users WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(permission) > 0 and permission[0][0] is not None:
        return permission[0][0]

    return 'user'


def set_user_permission(id, permission):
    conn, cursor = open_db()
    cursor.execute('''UPDATE users SET permissions = ? WHERE id = ?''', (permission, id,)).fetchall()
    conn.commit()
    close_db(conn, cursor)


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

    cursor.execute('''INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (str(uuid.uuid4()), data[0], data[1], data[2], data[3], 20 if len(data) < 5 else data[4], '' if len(data) < 6 else data[5],))
    conn.commit()
    close_db(conn, cursor)


def delete_mission(id):
    conn, cursor = open_db()

    reports = cursor.execute('''SELECT photo_id FROM reports WHERE mission_id = ?''', (id,)).fetchall()
    reports = [_[0] for _ in reports]

    for _ in reports:
        if _.isdigit() or not re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', _) is None:
            cursor.execute('''DELETE FROM media WHERE photo_id = ?;''', (_,))

    cursor.execute('''DELETE FROM reports WHERE mission_id = ?;''', (id,))
    cursor.execute('''DELETE FROM missions WHERE id = ?;''', (id,))
    conn.commit()

    close_db(conn, cursor)


def get_routes():
    conn, cursor = open_db()
    routes = cursor.execute('''SELECT id,name,buildings FROM routes''').fetchall()
    close_db(conn, cursor)

    if len(routes) > 0:
        routes = [(i[0], i[1], i[2]) for i in routes]
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


def get_route_buildings(id):
    conn, cursor = open_db()
    buildings = cursor.execute('''SELECT buildings FROM routes WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(buildings) > 0:
        return buildings[0][0]
    else:
        return 0




def get_addr_buildings(id, user_id=None):
    conn, cursor = open_db()
    addresses = None
    if user_id is None:
        addresses = cursor.execute('''SELECT addrs FROM routes WHERE id = ?''', (id,)).fetchall()
    else:
        addresses = cursor.execute('''SELECT routes.addrs FROM routes, missions WHERE missions.user = ? AND routes.id = missions.id_route AND missions.id = ?;''',
                                   (user_id, id, ))
    close_db(conn, cursor)

    if len(addresses) > 0 and addresses[0][0] is not None:
        return jsonpickle.decode(addresses[0][0])
    else:
        return 0

def check_can_delete_route(id):
    conn, cursor = open_db()
    rows = cursor.execute('''SELECT COUNT(id_route) FROM missions WHERE id_route = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(rows) > 0 and rows[0][0] > 0:
        return False
    else:
        return True


def delete_route(id):
    conn, cursor = open_db()
    cursor.execute('''DELETE FROM routes WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cursor)


def get_clerks():
    conn, cursor = open_db()
    users = cursor.execute('''SELECT id,username,permissions FROM users''').fetchall()
    close_db(conn, cursor)

    if len(users) > 0 and users[0][0] is not None:
        users = [(i[0], i[1], i[2]) for i in users]
    else:
        users = []
    return users


def get_admins():
    conn, cursor = open_db()
    users = cursor.execute('''SELECT id FROM users WHERE permissions = ?''', (sett.permissions[0],)).fetchall()
    close_db(conn, cursor)

    if len(users) > 0 and users[0][0]:
        return [int(i[0]) for i in users]

    return []


def get_clerk_by_id(id):
    conn, cursor = open_db()
    user = cursor.execute('''SELECT id,username,earned FROM users WHERE id = ?''', (id,)).fetchall()
    not_proof = cursor.execute('''SELECT SUM(reward) FROM missions WHERE status = 1 AND proof = 0 AND user = ?''',
                               (id,)).fetchall()
    close_db(conn, cursor)

    if len(user) > 0 and user[0][0] is not None:
        user = list(user[0])
        user.append(not_proof[0][0] if (len(not_proof) > 0 and not_proof[0][0] is not None) else 0)
    else:
        user = []
    return user


def get_mission_by_id(id, not_completed=False):
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


def get_route_id_by_mission(id):
    conn, cursor = open_db()
    route_id = cursor.execute('''SELECT id_route FROM missions WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    if len(route_id) > 0 and route_id[0][0] is not None:
        route_id = route_id[0][0]
    else:
        route_id = None
    return route_id


def get_missions_by_user_id(user_id):
    conn, cursor = open_db()
    missions = cursor.execute('''SELECT id,comment,status,proof FROM missions WHERE user = ? AND proof = "0"''',
                              (user_id,)).fetchall()
    close_db(conn, cursor)

    data_missions = []
    if len(missions) > 0 and missions[0][0] is not None:
        data_missions = [(i[0], i[1], i[2], i[3]) for i in missions]

    return data_missions


def get_coords_mission_by_id(id):
    conn, cursor = open_db()
    coords = cursor.execute('''SELECT coords FROM routes WHERE id = ?''', (id,)).fetchall()
    close_db(conn, cursor)

    data_missions = ''
    if len(coords) > 0 and coords[0][0] is not None:
        data_missions = jsonpickle.decode(coords[0][0])

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


def get_count_reports_mission(id, id_building=None):
    conn, cursor = open_db()
    count = None
    if not id_building is None:
        count = cursor.execute('''SELECT COUNT() FROM reports WHERE mission_id = ? AND building_id = ?''',
                               (id, id_building,)).fetchall()
    else:
        count = cursor.execute('''SELECT COUNT() FROM reports WHERE mission_id = ?''',
                               (id,)).fetchall()
    close_db(conn, cursor)

    if len(count) > 0 and count[0][0] is not None:
        count = count[0][0]

    return count


def delete_media_by_group_id(id):
    conn, cursor = open_db()
    cursor.execute('''DELETE FROM media WHERE photo_id = ?''', (id,))
    conn.commit()
    close_db(conn, cursor)


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


def get_coords_buildings(mission_id, user_id):
    conn, cursor = open_db()
    location = cursor.execute('''SELECT routes.coords FROM routes, missions WHERE missions.user = ? AND routes.id = missions.id_route AND missions.id = ?;''',
                              (user_id, mission_id,)).fetchall()
    close_db(conn, cursor)

    if len(location) > 0 and location[0][0] is not None:
        return jsonpickle.decode(location[0][0])

    return {}


def save_report_user(id, user_id, location, photo_id, video_id, building_id, type_rep):
    conn, cursor = open_db()
    location = jsonpickle.encode(location)
    cursor.execute('''INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (id, user_id, location, photo_id, video_id,
                    int(datetime.datetime.timestamp(datetime.datetime.now())), building_id, type_rep,))
    cursor.execute('''UPDATE missions SET reward = reward + ? WHERE id = ?''', (get_costs()[int(type_rep)][1], id))
    conn.commit()


def complete_mission(id):
    conn, cur = open_db()
    cur.execute('''UPDATE missions SET status = "1" WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def change_mission(id, user, name, reward, reports, date):
    conn, cur = open_db()
    cur.execute(
        '''UPDATE missions SET user = ?, comment = ?, reward = ?, count_reports=?, date_expire=? WHERE id = ?''',
        (user, name, reward, reports, date, id,))
    conn.commit()
    close_db(conn, cur)


def add_photo_to_media(msg_id, file_id, hash):
    conn, cur = open_db()
    cur.execute('''INSERT INTO media VALUES (?, ?, ?)''', (msg_id, file_id, hash, ))
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


def check_file_hash(hash):
    conn, cur = open_db()
    count_dublicates = cur.execute('''SELECT count() FROM media WHERE hash = ?''', (hash,)).fetchall()
    close_db(conn, cur)

    if len(count_dublicates) > 0 and count_dublicates[0][0] is not None and count_dublicates[0][0] > 0:
        return False
    else:
        return True


def change_balance_clerk(id, balance):
    conn, cur = open_db()
    cur.execute('''UPDATE users SET earned = ? WHERE id = ?''', (balance, id,))
    conn.commit()
    close_db(conn, cur)


def kick_user(id):
    conn, cur = open_db()
    cur.execute('''DELETE FROM users WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def proof_mission(id):
    conn, cur = open_db()
    user, reward = cur.execute('''SELECT user,reward FROM missions WHERE id = ?''', (id,)).fetchall()[0]
    cur.execute('''UPDATE users SET earned = earned + ? WHERE id = ?''', (reward, user,))
    cur.execute('''UPDATE missions SET proof = 1, status = 1 WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def retry_mission_by_id(id):
    conn, cur = open_db()
    cur.execute('''UPDATE missions SET date_expire = 
                        (CASE WHEN date_expire >= DATETIME("now") THEN DATETIME(date_expire, "+1 day") ELSE DATETIME("now", "start of day", "+3 days", "-1 second") END)
                        WHERE id = ?''', (id,))
    cur.execute('''UPDATE missions SET status = 0, proof = 0 WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def reject_mission_by_id(id):
    conn, cur = open_db()
    mission = cur.execute('''SELECT status, proof, reward, user FROM missions WHERE id = ?''', (id,)).fetchall()[0]
    cur.execute('''UPDATE users SET earned = earned - (CASE WHEN (? = 1 AND ? = 1) THEN ? ELSE 0 END)
                    WHERE id = ?''', *(mission,))
    cur.execute('''UPDATE missions SET status = 0,proof = 1 WHERE id = ?''', (id,))
    conn.commit()
    close_db(conn, cur)


def get_reports_by_id(id, user_id=None):
    conn, cur = open_db()
    reports = ''
    if user_id is None:
        reports = cur.execute(
        '''SELECT location,photo_id,video_id,[date],building_id FROM reports WHERE mission_id = ? ORDER BY [date] ASC;''',
        (id,)).fetchall()
    else:
        reports = cur.execute(
        '''SELECT location,photo_id,video_id,[date],building_id FROM reports WHERE mission_id = ? AND user_id = ? ORDER BY [date] ASC;''',
        (id, user_id, )).fetchall()
    close_db(conn, cur)

    if len(reports) > 0 and reports[0][0] is not None:
        ids = [[i[0], i[1], i[2], i[3], i[4]] for i in reports]
    else:
        return []

    return ids


def delete_report(date, id_user):
    conn, cur = open_db()
    report_info = cur.execute(
        '''SELECT mission_id,type FROM reports WHERE [date] = ?''',
        (date,)).fetchall()[0]
    cur.execute('''UPDATE missions SET reward = reward - ? WHERE id = ? AND [user] = ?''',
                (get_costs()[report_info[1]][1], report_info[0], id_user,))
    cur.execute('''DELETE FROM reports WHERE mission_id = ? AND user_id = ? AND [date] = ?''',
                (report_info[0], id_user, date))
    conn.commit()
    close_db(conn, cur)


def get_min_route(points: dict):
    distances = {}

    for idx in points.keys():
        distances[idx] = {}

        for id, point in points.items():
            if id != idx:
                distances[idx][id] = get_length_locations(point[0], point[1], points[idx][0], points[idx][1])

        distances[idx] = sorted(distances[idx].items(), key=lambda kv: kv[1])

    route = []

    def min_route(distance, curr_id_point, route: list = []):

        id = min(distances[curr_id_point], key=lambda kv: kv[1])

        route.append(curr_id_point)
        distances.pop(curr_id_point)
        for idx in distances.keys():
            distances[idx] = [i for i in distances[idx] if i[0] != curr_id_point]

        if len(distances) > 0 and not [] in distance.values():
            return min_route(distance, id[0], route)
        else:
            route.append(list(distance.keys())[-1])
            return route

    return min_route(distances, 0)


def get_costs():
    conn, cur = open_db()
    costs = cur.execute('''SELECT * FROM types_cost ORDER BY [id] ASC''').fetchall()
    close_db(conn, cur)

    costs = {i[0]: (i[1], i[2]) for i in costs}

    return costs


def change_costs(costs: dict):
    conn, cur = open_db()
    for i in costs.keys():
        cur.execute('''UPDATE types_cost SET cost = ? WHERE id = ?;''', (costs[i], i,))

    conn.commit()
    close_db(conn, cur)


#TO#DO: добавить проверку времени между отчетами
def check_coordinates(id_mission, lat, lon):
    conn, cur = open_db()
    id_route = cur.execute('''SELECT id_route FROM missions WHERE id = ?''', (id_mission,)).fetchall()[0][0]
    coords = cur.execute('''SELECT coords FROM routes WHERE id = ?''', (id_route,)).fetchall()
    last_report= cur.execute('''SELECT location,MAX(date) FROM reports WHERE mission_id = ?''', (id_mission,)).fetchall()
    close_db(conn, cur)
    coords = jsonpickle.decode(coords[0][0])

    for pos in coords.values():
        # print(get_length_locations(lat, lon, pos[0], pos[1]), lat, lon, pos[0], pos[1])
        if get_length_locations(lat, lon, pos[0], pos[1]) <= sett.allow_radius:
            if len(last_report) and last_report[0][0] is not None:
                current_time_h = int(datetime.datetime.timestamp(datetime.datetime.now())) / 60. / 60.
                last_time_h = int(last_report[0][1]) / 60. / 60.
                max_distance_allow_speed = sett.allow_speed * (current_time_h - last_time_h)
                last_coords = jsonpickle.decode(last_report[0][0])
                current_distance = get_length_locations(lat, lon, last_coords[0], last_coords[1])
                if current_distance >= max_distance_allow_speed:
                    return 2
            return 0
    return 1


def get_length_locations(lat1, lon1, lat2, lon2):
    def degrees_to_rads(deg):
        return (deg * math.pi) / 180.0

    lat1 = degrees_to_rads(lat1)
    lat2 = degrees_to_rads(lat2)
    lon1 = degrees_to_rads(lon1)
    lon2 = degrees_to_rads(lon2)
    return 2 * 6371 * math.asin(math.sqrt(
        math.pow(math.sin(((lat2 - lat1) / 2.0)), 2.0) +
        math.cos(lat1) * math.cos(lat2) *
        math.pow(math.sin(((lon2 - lon1) / 2.0)), 2.0)
    ))


def execute_db(command):
    conn, cur = open_db()
    cur.execute(command)
    conn.commit()
    close_db(conn, cur)


# скачивание файла с сервера телеграмм
def download_file(file_id):
    get_file_link = f'https://api.telegram.org/bot{sett.API_KEY}/getFile?file_id={file_id}'

    r = requests.get(get_file_link)

    for _ in range(0, 5):
        if r.status_code == 200:
            file_path = r.json()['result']['file_path']
            download_file_raw = f'https://api.telegram.org/file/bot{sett.API_KEY}/{file_path}'

            r_data = requests.get(download_file_raw)

            if r_data.status_code == 200:
                return r_data.content  # base64.b64encode(r_data.text.encode('utf-8'))

    return None


def check_user_trusted(user_id):
    conn, cur = open_db()
    trusted = cur.execute('''SELECT trusted FROM users WHERE id = ?''', (user_id, )).fetchall()
    close_db(conn, cur)

    if len(trusted) > 0:
        return True if str(trusted[0][0]) == '1' else False

    return False


def check_rekrut_form(user_id):
    conn, cur = open_db()
    form = cur.execute('''SELECT * FROM forms WHERE user_id = ?''', (user_id, )).fetchall()
    close_db(conn, cur)

    if len(form) > 0:
        return True

    return False


def save_rekrut(user_id, full_name, birthday, local_region, qualities, info, reward, photo_id):
    conn, cur = open_db()
    cur.execute('''INSERT INTO forms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (str(uuid.uuid4()), user_id, datetime.datetime.now().timestamp(), full_name, birthday, local_region,
                 qualities, info, reward, photo_id, ))
    conn.commit()
    close_db(conn, cur)


def get_rekruts(all=None):
    form = ''
    conn, cur = open_db()
    if all is None:
        form = cur.execute(
            '''SELECT forms.id, forms.full_name, users.trusted FROM forms,users WHERE users.id = forms.user_id AND users.trusted = "0"''').fetchall()
    else:
        form = cur.execute('''SELECT forms.id, forms.full_name, users.trusted FROM forms,users WHERE users.id = forms.user_id''').fetchall()
    close_db(conn, cur)

    return list(form)


def get_rekrut_info(id):
    conn, cur = open_db()
    form = cur.execute(
        '''SELECT users.username, forms.*, users.trusted FROM forms,users WHERE forms.id = ? AND users.id = forms.user_id''', (id, )).fetchall()
    close_db(conn, cur)

    return list(form)


def pass_rekrut(user_id):
    conn, cur = open_db()
    cur.execute(
        '''UPDATE users SET trusted = "1" WHERE id = ?''',
        (user_id,))
    conn.commit()
    close_db(conn, cur)


# Генерация псевдослучайных чисел задание зерна
rd = random.Random()
rd.seed(datetime.datetime.now().microsecond)
uuid.UUID(int=rd.getrandbits(128))

if __name__ == '__main__':
    delete_mission('d009da59-b52d-450b-b118-7dc073e10142')
