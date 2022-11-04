import os

cookie_secret_key = '4b87e6fb926784872a022fd6fff0c6f97a71677e44ce1102125ea97098b1959c' if os.environ.get('COOKIE_KEY') is None else os.environ.get('API_KEY')
API_KEY = '5606301926:AAHGRUqdLVEcaxhbIKepJA5ttOUISqVgOys' if os.environ.get('API_KEY') is None else os.environ.get('API_KEY')  # Никому не сообщать, получать в @BotFather
#5408023773:AAHSVnYvXURWLG5Qj_dJjUIk37_l7oZgfrU
sqlite_file = os.path.join(os.getcwd(), 'data.sqlite')
file_report_path = os.path.join(os.getcwd(), 'report_{}_{}.zip')

WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_URL_BASE = "https://bdfix.ru/delivery_bot"
WEBHOOK_URL_PATH = "/%s/" % (API_KEY)

allow_radius = 2.0  # допустимый радиус отправки от нод геолокации в км
allow_speed = 50  # допустимая корость перемещения между точками в км/ч

info_user_text = 'Пользователь: <b>@{}</b>\n\n' \
                 'Баланс: <u><b>{}</b></u> руб.\n' \
                 'Не подтвержденный баланс: <b>{}</b> руб.\n\n' \
                 '<u>Миссии:</u>\n' \
                 '{}' \

info_proof_mission_text = 'Выполнил: <b>@{}</b>\n' \
                          'Задание: <b>{}</b>\n\n' \
                          'Вознаграждение: <b>{}</b>\n' \
                          'Количество отчетов <b>{}</b> из <b>{}</b>\n' \
                          'Время окончания: {}\n' \
                          'Статус: {}'

permissions = {
    0: 'admin',
    1: 'moder',
    2: 'user'
}
