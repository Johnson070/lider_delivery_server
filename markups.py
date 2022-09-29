import math

from telebot import types
import functions as func


def get_clerk_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Задания", callback_data='quests_user'),
        types.InlineKeyboardButton('Информация', callback_data='information')
    )

    return markup


def get_admin_menu(full_menu=False):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Маршруты", callback_data='routes'),
        types.InlineKeyboardButton('Работники', callback_data='clerks'),
        row_width=2
    )

    markup.add(types.InlineKeyboardButton('Выполненые задания', callback_data='completed_quests_0'))
    markup.add(types.InlineKeyboardButton('Задания', callback_data='all_quests_0'))

    markup.add(
        types.InlineKeyboardButton('Статистика', callback_data='stats'),
        types.InlineKeyboardButton('Ссылка на приглашения', callback_data='invite_link')
    )
    markup.add(types.InlineKeyboardButton('Тест webapp', web_app=types.WebAppInfo('https://127.0.0.1/auth')))

    if func.count_invite_links() > 0:
        markup.add(types.InlineKeyboardButton('Сбросить все ссылки', callback_data='reset_links'))
    if full_menu:
        markup.add(
            types.InlineKeyboardButton('Скачать DB', callback_data='download_db'),
            types.InlineKeyboardButton('Скачать Бота', callback_data='download_bot'),
            row_width=1
        )
    return markup


def get_routes_menu(page, id_user = None):
    markup = types.InlineKeyboardMarkup()
    routes = func.get_routes()
    max_pages = math.ceil(len(routes) / 10)

    prefix = 'routes_' if id_user is None else f'add_user_mission_{id_user}_'
    back_callback = 'back_admin' if id_user is None else f'user_info_{id_user}'

    if id_user is None:
        markup.add(types.InlineKeyboardButton('Добавить маршрут', callback_data='add_route'))

    if routes:
        markup.add(
            *[types.InlineKeyboardButton(i[1],
        callback_data=f'{"routes_" if id_user is None else "select_route_"}{i[0]}{"" if id_user is None else f"_{id_user}"}')
              for i in routes[0 + (page * 10):10 + (page * 10)]],
            row_width=1
        )
    if page == 0 and max_pages > 1:
        markup.add(
            types.InlineKeyboardButton('Назад', callback_data=back_callback),
            types.InlineKeyboardButton('=>', callback_data=f'{prefix}{page + 1}')
        )
    elif 0 < page < (max_pages - 1):
        markup.add(
            types.InlineKeyboardButton('<=', callback_data=f'{prefix}{page - 1}'),
            types.InlineKeyboardButton('Назад', callback_data=back_callback),
            types.InlineKeyboardButton('=>', callback_data=f'{prefix}{page + 1}'),
            row_width=3
        )
    elif 0 < page < max_pages:
        markup.add(
            types.InlineKeyboardButton('<=', callback_data=f'{prefix}{page - 1}'),
            types.InlineKeyboardButton('Назад', callback_data=back_callback)
        )
    else:
        markup.add(types.InlineKeyboardButton('Назад', callback_data=back_callback))

    return markup


# TODO: сделать проверку что маршрут нигде не используется
def info_route_menu(id, route_url=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Удалить', callback_data=f'delete_route_{id}'),
        types.InlineKeyboardButton('Назад', callback_data='back_admin')
    )
    if route_url is not None:
        markup.add(
            types.InlineKeyboardButton('Посмотреть', web_app=types.WebAppInfo(route_url))
        )
    return markup


def back_admin_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back_admin'))
    return markup


def back_cleck_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад', callback_data='start'))
    return markup


def get_clerks_menu(page):
    markup = types.InlineKeyboardMarkup()
    clerks = func.get_clerks()

    max_pages = math.ceil(len(clerks) / 10)

    if clerks:
        markup.add(
            *[types.InlineKeyboardButton(i[1], callback_data=f'user_info_{i[0]}')
              for i in clerks[0 + (page * 10):10 + (page * 10)]],
            row_width=1
        )
    if page == 0 and max_pages > 1:
        markup.add(
            types.InlineKeyboardButton('Назад', callback_data='back_admin'),
            types.InlineKeyboardButton('=>', callback_data=f'clerk_page_{page + 1}')
        )
    elif 0 < page < (max_pages - 1):
        markup.add(
            types.InlineKeyboardButton('<=', callback_data=f'clerk_page_{page - 1}'),
            types.InlineKeyboardButton('Назад', callback_data='back_admin'),
            types.InlineKeyboardButton('=>', callback_data=f'clerk_page_{page + 1}'),
            row_width=3
        )
    elif 0 < page < max_pages:
        markup.add(
            types.InlineKeyboardButton('<=', callback_data=f'clerk_page_{page - 1}'),
            types.InlineKeyboardButton('Назад', callback_data='back_admin')
        )
    else:
        markup.add(types.InlineKeyboardButton('Назад', callback_data='back_admin'))

    return markup


def get_clerk_control_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    # TODO: сделать добавление одного дня к работе
    #  также сделать редактор миссии
    markup.add(
        types.InlineKeyboardButton('Добавить миссию', callback_data=f'add_user_mission_{user_id}'),
        types.InlineKeyboardButton('Удалить миссию', callback_data=f'remove_user_mission_{user_id}'),
        types.InlineKeyboardButton('Изменить баланс', callback_data=f'change_balance_{user_id}'),
        row_width=2
    )
    markup.add(
        types.InlineKeyboardButton('Исключить', callback_data=f'kick_{user_id}'),
        types.InlineKeyboardButton('Назад', callback_data=f'clerks')
    )

    return markup


def back_to_clerk_menu(id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data=f'user_info_{id}')
    )
    return markup


# def select_route_to_clerk(id, route_preffix='select_route_'):
#     routes = func.get_routes()
#     markup = types.InlineKeyboardMarkup(row_width=1)
#     markup.add(
#         *[types.InlineKeyboardButton(i[1], callback_data=f'{route_preffix}{i[0]}_{id}') for i in routes],
#         row_width=2
#     )
#     markup.add(
#         types.InlineKeyboardButton('Назад', callback_data=f'user_info_{id}'),
#         row_width=1
#     )
#     return markup


def get_missons_clerk_by_id(id, route_preffix='select_route_'):
    clerk = func.get_clerk_by_id(id)
    missions = [(i[0], i[1]) for i in func.get_missions_by_user_id(id)]

    markup = types.InlineKeyboardMarkup()
    markup.add(
        *[types.InlineKeyboardButton(i[1], callback_data=f'{route_preffix}{i[0]}_{id}') for i in missions],
        row_width=2
    )
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data=f'user_info_{id}'),
        row_width=1
    )
    return markup


def missions_by_user_id_menu(user_id):
    markup = types.InlineKeyboardMarkup()

    missions = func.get_missions_by_user_id(user_id)
    if missions:
        markup.add(
            *[types.InlineKeyboardButton(i[1], callback_data=f'quest_user_{i[0]}') for i in missions],
            row_width=2
        )
    markup.add(types.InlineKeyboardButton('Назад', callback_data='start'))

    return markup


def mission_menu(mission_id, expired, route_url=None):
    markup = types.InlineKeyboardMarkup()
    if not expired:
        markup.add(
            types.InlineKeyboardButton('Добавить отчет', callback_data=f'report_mission_{mission_id}'),
            types.InlineKeyboardButton('Завершить', callback_data=f'complete_{mission_id}')
        )

    if route_url is not None:
        markup.add(
            types.InlineKeyboardButton('Посмотреть на карте', web_app=types.WebAppInfo(route_url))
        )
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data='start_del')
    )
    return markup


def get_location_menu():
    markup = types.ReplyKeyboardMarkup()

    markup.add(
        types.KeyboardButton('Отправить геолокацию', request_location=True),
        row_width=1
    )

    return markup


def get_missions_menu(page, with_not_completed=False):
    markup = types.InlineKeyboardMarkup()
    missions = func.get_missions(with_not_completed)

    max_pages = math.ceil(len(missions) / 10)

    prefix = 'completed_quests_' if not with_not_completed else 'all_quests_'

    if missions:
        markup.add(
            *[types.InlineKeyboardButton(i[1], callback_data=f'mission_report_{i[0]}_#')
              for i in missions[0 + (page * 10):10 + (page * 10)]],
            row_width=1
        )
    if page == 0 and max_pages > 1:
        markup.add(
            types.InlineKeyboardButton('Назад', callback_data='back_admin'),
            types.InlineKeyboardButton('=>', callback_data=f'{prefix}{page + 1}')
        )
    elif 0 < page < (max_pages - 1):
        markup.add(
            types.InlineKeyboardButton('<=', callback_data=f'{prefix}{page - 1}'),
            types.InlineKeyboardButton('Назад', callback_data='back_admin'),
            types.InlineKeyboardButton('=>', callback_data=f'{prefix}{page + 1}'),
            row_width=3
        )
    elif 0 < page < max_pages:
        markup.add(
            types.InlineKeyboardButton('<=', callback_data=f'{prefix}{page - 1}'),
            types.InlineKeyboardButton('Назад', callback_data='back_admin')
        )
    else:
        markup.add(types.InlineKeyboardButton('Назад', callback_data='back_admin'))

    return markup


def check_report_menu(id, proof=False, rejected=False, back_to_all=False):
    markup = types.InlineKeyboardMarkup()

    if not proof and not rejected:
        markup.add(
            types.InlineKeyboardButton('Перевести в выполненные', callback_data=f'to_proof_{id}')
        )

        markup.add(
            types.InlineKeyboardButton('Скачать отчет(zip)', callback_data=f'download_rep_{id}'),
            types.InlineKeyboardButton('На доработку(+1 день)', callback_data=f'retry_rep_{id}')
        )

        markup.add(
            types.InlineKeyboardButton('Забраковать', callback_data=f'reject_{id}'),
        )
    elif proof and not rejected:
        markup.add(
            types.InlineKeyboardButton('Скачать отчет(zip)', callback_data=f'download_rep_{id}'),
            types.InlineKeyboardButton('Забраковать(⚠️)', callback_data=f'reject_{id}')
        )
    elif rejected:
        markup.add(
            types.InlineKeyboardButton('Перевести в выполненные', callback_data=f'to_proof_{id}')
        )
        markup.add(
            types.InlineKeyboardButton('Скачать отчет(zip)', callback_data=f'download_rep_{id}'),
            types.InlineKeyboardButton('На доработку(+1 день)', callback_data=f'retry_rep_{id}'),
            row_width=2
        )
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data=('completed_quests_0' if not back_to_all else 'all_quests_0'))
    )

    return markup
