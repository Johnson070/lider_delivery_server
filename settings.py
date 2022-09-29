import os

def up_directory(path):
    path = path.split('\\')
    path.pop()
    return '\\'.join(path)


API_KEY = '5408023773:AAHSVnYvXURWLG5Qj_dJjUIk37_l7oZgfrU'  # Никому не сообщать, получать в @BotFather
sqlite_file = os.path.join(up_directory(os.getcwd()), 'data.sqlite')
file_report_path = os.path.join(os.getcwd(), 'report_{}_{}.zip')

allow_radius = 1.0 # допустимый радиус отправки от нод геолокации в км

info_user_text = 'Пользователь: <b>@{}</b>\n\n' \
                 'Баланс: <u><b>{}</b></u> руб.\n' \
                 'Не потвержденный баланс: <b>{}</b> руб.\n\n' \
                 '<u>Миссии:</u>\n' \
                 '{}' \

info_proof_mission_text = 'Выполнил: <b>@{}</b>\n' \
                          'Задание: <b>{}</b>\n\n' \
                          'Вознаграждение: <b>{}</b>\n' \
                          'Количество отчетов <b>{}</b> из <b>{}</b>\n' \
                          'Время окончания: {}\n' \
                          'Статус: {}'

admins = [425637878, 2007858008,5243958813]  # id чатов кто имеет права администратора
