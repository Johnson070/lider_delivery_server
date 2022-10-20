import datetime
import re
import jsonpickle, uuid
import functions as func
import settings as sett

from bot_tg import bot


class geo_json:
    class point:
        def __init__(self, coords, id, uuid=None, time=None, building_id=None):
            self.type = 'Feature'
            self.id = id
            self.geometry = {
                'coordinates': coords,
                'type': 'Point'
            }
            self.properties = {
                'iconCaption': f'Отчет #{id}',
                'iconContent': id,
                'marker-color': '#1e98ff',
                'uuid': uuid,
                'id':id,
                'building':building_id,
                'unix': time
            }

    class line_string:
        def __init__(self, coords, id):
            self.type = 'Feature'
            self.id = id
            self.geometry = {
                'coordinates': coords,
                'type': 'LineString'
            }
            self.properties = {
                "stroke":"#ed4543",
                "stroke-width":"5",
                "stroke-opacity":0.9,
            }

    def __init__(self, points):
        self.type = 'FeatureCollection'
        self.metadata = {
            'name': 'Отчет',
            'creator': 'Yandex Map Constructor'
        }
        self.features = points


def get_raw_by_id(id):
    _ = bot.get_file(id)
    _ = bot.download_file(_.file_path)

    return _


def get_report(id):
    mission = func.get_full_info_mission(id)
    count_reports = func.get_count_reports_mission(id)
    buildings = func.get_route_buildings(mission[3])
    user = func.get_clerk_by_id(mission[1])[1]

    data = func.get_reports_by_id(id)

    reports = ''
    report = '''
        <div class="report">
            <p>
                Отчет №{0}<br>
                Дом {1}<br>
                {2}<br>
                {3}
            </p>
            <div class="media">
                {4}
            </div>
        </div>
    '''
    img = '''<div class='report-img'><img src="data:image/png;base64, {0}" /></div>'''
    video = '''<div class='report-img'><iframe src="data:video/mp4;base64, {0}"  autoplay=0/></div>'''

    def bytes_to_base64_string(value: bytes) -> str:
        import base64
        return base64.b64encode(value).decode('ASCII')

    count_reports = len(data)
    for _ in range(0, count_reports):
        addrs = func.get_addr_buildings(mission[3])
        photos_ids = None
        if data[_][1].isdigit() or not re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', data[_][1]) is None:
            photos_ids = func.get_photos_by_media_id(data[_][1])
        else:
            photos_ids = [data[_][1]]

        medias = ''
        for num in range(0, len(photos_ids)):
            medias += img.format(bytes_to_base64_string(func.download_file(photos_ids[num])))
        # medias += video.format(bytes_to_base64_string(func.download_file(data[_][2])))

        reports += report.format(_+1, data[_][4]+1, datetime.datetime.fromtimestamp(data[_][3]), addrs[str(data[_][4])], medias)

    from server_flask import render_template
    return render_template('report_template.html',
                           reports=reports,
                           user=user,
                           name_mission=mission[2],
                           reward=mission[6],
                           count=count_reports,
                           all_count=mission[5],
                           buildings=buildings,
                           status='✅ Выполнено' if (mission[7] and mission[8]) else
                           ('⚠️ Ожидает подтверждения' if (mission[7] and not mission[8]) else
                            ('❗️❗️Забраковано' if (not mission[7] and mission[8]) else '❌ Не выполнено')))


def get_geojson(id):
    data = func.get_reports_by_id(id)
    count_reports = len(data)
    points = []

    for _ in data:
        points.append(jsonpickle.decode(_[0])[::-1])

    data = [geo_json.point(points[i - 1], i, id, data[i-1][3], data[i-1][4]) for i in range(1, count_reports + 1)]
    try:
        data.append(geo_json.line_string(points, data[-1].id+1))
    except:
        pass
    geojson = geo_json(data)

    return jsonpickle.encode(geojson, unpicklable=False)


def get_center_map(id):
    data = func.get_reports_by_id(id)
    count_reports = len(data)
    points = [0,0]

    for _ in data:
        point = jsonpickle.decode(_[0])
        points[0] += point[0]
        points[1] += point[1]

    if points == [0,0]:
        return jsonpickle.encode([30.19,59.57], unpicklable=False)
    else:
        points[0] = points[0] / count_reports
        points[1] = points[1] / count_reports

    return jsonpickle.encode(points[::-1], unpicklable=False)

if __name__ == '__main__':
    from flask import Flask, render_template, Response
    import os


    project_root = os.path.dirname(os.path.realpath('__file__'))
    template_path = os.path.join(project_root, 'templates')
    static_path = os.path.join(project_root, 'static')
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)



    @app.route('/users', methods=['GET'])
    def test_pdf():

        return get_report('34f0cb62-b47e-46b3-b981-6c3a43c293be')


    app.run(host='127.0.0.1',port=8080, debug=True)
    #get_report('34f0cb62-b47e-46b3-b981-6c3a43c293be')
