import zipfile, jsonpickle, uuid
import functions as func
import settings as sett

from bot_tg import bot


class geo_json:
    class point:
        def __init__(self, coords, id):
            self.type = 'Feature'
            self.id = id
            self.geometry = {
                'coordinates': coords,
                'type': 'Point'
            }
            self.properties = {
                'iconCaption': f'Отчет #{id}',
                'iconContent': id,
                'marker-color': '#1e98ff'
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
    file_name = sett.file_report_path.format(id, uuid.uuid4())
    report = zipfile.ZipFile(file_name, 'w')

    data = func.get_reports_by_id(id)
    count_reports = len(data)
    points = []

    for _ in range(0, count_reports):
        points.append(jsonpickle.decode(data[_][0]))
        photos_ids = None
        if data[_][1].isdigit():
            photos_ids = func.get_photos_by_media_id(data[_][1])
        else:
            photos_ids = [data[_][1]]

        report.writestr(f'Отчет #{_ + 1}/video_note.mp4', get_raw_by_id(data[_][2]))

        for num in range(0, len(photos_ids)):
            report.writestr(f'Отчет #{_ + 1}/photo_report_{num}.png', get_raw_by_id(photos_ids[num]))

    points = [geo_json.point(points[i - 1], i) for i in range(1, count_reports + 1)]
    geojson = geo_json(points)
    report.writestr(f'yandex_map_json_points.geojson', jsonpickle.encode(geojson, unpicklable=False))

    report.close()

    return file_name

# if __name__ == '__main__':
#     bot = telebot.TeleBot(sett.API_KEY)
#
#     @bot.message_handler(regexp='test_zip_(([a-f0-9]+-){4}([a-f0-9]+))$')
#     def test_send_zip(msg):
#         get_report(bot, re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', msg.text).group(0))
#         pass
#
#     bot.polling(none_stop=True, interval=0, timeout=2000)