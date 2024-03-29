import math

from telebot import types
import functions as func
import settings as sett


def get_clerk_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Панель пользователя', web_app=types.WebAppInfo(sett.WEBHOOK_URL_BASE + '/user/auth'))
    )

    return markup


def get_moder_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Панель администрирования', web_app=types.WebAppInfo(sett.WEBHOOK_URL_BASE + '/moder/auth'))
    )
    return markup


def get_link_permissions():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        *[types.InlineKeyboardButton(value, callback_data=f'invite_link_{key}')
          for key, value in sorted(sett.permissions.items(), reverse=True)]
    )
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data='back_admin')
    )
    return markup


def get_admin_menu(full_menu=False, role=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Ссылка на приглашения', callback_data='invite_link')
    )

    markup.add(types.InlineKeyboardButton('Админ панель', web_app=types.WebAppInfo(sett.WEBHOOK_URL_BASE + '/auth' + (f'_{role}' if role is not None and role != 'admin' else '')))) #sett.WEBHOOK_URL_BASE +
    if func.count_invite_links() > 0:
        markup.add(types.InlineKeyboardButton('Сбросить все ссылки', callback_data='reset_links'))
    if full_menu:
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
        markup.add(
            types.InlineKeyboardButton('Скачать DB', callback_data='download_db'),
            types.InlineKeyboardButton('Скачать Бота', callback_data='download_bot'),
            row_width=1
        )
    return markup


def end_send_media(callback_data):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Отменить отправку отчета', callback_data=callback_data)
    )

    return markup


def get_routes_menu(page, id_user = None):
    markup = types.InlineKeyboardMarkup()
    routes = func.get_routes()
    max_pages = math.ceil(len(routes) / 10)

    prefix = 'route_' if id_user is None else f'add_user_mission_{id_user}_'
    back_callback = 'back_admin' if id_user is None else f'user_info_{id_user}'

    if id_user is None:
        markup.add(types.InlineKeyboardButton('Добавить маршрут', callback_data='add_route'))

    if routes:
        markup.add(
            *[types.InlineKeyboardButton(i[1],
        callback_data=f'{"route_" if id_user is None else "select_route_"}{i[0]}{"" if id_user is None else f"_{id_user}"}')
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


def info_route_menu(id, route_url=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if func.check_can_delete_route(id):
        markup.add(types.InlineKeyboardButton('Удалить', callback_data=f'delete_route_{id}'), row_width=2)
    if route_url is not None:
        markup.add(
            types.InlineKeyboardButton('Посмотреть', web_app=types.WebAppInfo(route_url)),
            row_width=2
        )
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data='back_admin')
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


def select_user_building(building_id, id, last_building):
    markup = types.InlineKeyboardMarkup()

    if last_building != 0:
        markup.add(
            types.InlineKeyboardButton('Следующий дом',
                                       callback_data=f'building_{str(building_id + 1) if (building_id + 1) != last_building else "0"}_{id}'),
            row_width=1
        )

        markup.add(
            types.InlineKeyboardButton('Предыдущий дом',
                                       callback_data=f'building_{str(building_id - 1) if building_id > 0 else str(last_building-1)}_{id}'),
            row_width=1
        )

    markup.add(
        types.InlineKeyboardButton('Добавить отчет для подъезда', callback_data=f'select_type_{building_id}_{id}'),
        types.InlineKeyboardButton('Назад', callback_data=f'quests_user_back_{id}'),
        row_width=1
    )

    return markup


def mission_menu(mission_id, expired, route_url=None):
    markup = types.InlineKeyboardMarkup()
    if not expired:
        markup.add(
            types.InlineKeyboardButton('Добавить отчет', callback_data=f'report_mission_{mission_id}')
        )

    if route_url is not None:
        markup.add(
            types.InlineKeyboardButton('Посмотреть на карте', web_app=types.WebAppInfo(route_url))
        )

    if not expired:
        markup.add(types.InlineKeyboardButton('Завершить', callback_data=f'confirm_{mission_id}'))
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data='start_del')
    )
    return markup


def confirm_end_mission(id):
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton('Подтвердить', callback_data=f'complete_{id}'),
        types.InlineKeyboardButton('Назад', callback_data=f'quests_user_back_{id}'),
        row_width=2
    )

    return markup


def get_location_menu():
    markup = types.ReplyKeyboardMarkup()

    markup.add(
        types.KeyboardButton('Отправить геолокацию', web_app=types.WebAppInfo(sett.WEBHOOK_URL_BASE + '/location')), #sett.WEBHOOK_URL_BASE +
        types.KeyboardButton('Назад'),
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
            types.InlineKeyboardButton('Скачать отчет', callback_data=f'download_rep_{id}'),
            types.InlineKeyboardButton('На доработку(+1 день)', callback_data=f'retry_rep_{id}')
        )

        markup.add(
            types.InlineKeyboardButton('Забраковать', callback_data=f'reject_{id}'),
        )
    elif proof and not rejected:
        markup.add(
            types.InlineKeyboardButton('Скачать отчет', callback_data=f'download_rep_{id}'),
            types.InlineKeyboardButton('Забраковать', callback_data=f'reject_{id}')
        )
    elif rejected:
        markup.add(
            types.InlineKeyboardButton('Перевести в выполненные', callback_data=f'to_proof_{id}')
        )
        markup.add(
            types.InlineKeyboardButton('Скачать отчет', callback_data=f'download_rep_{id}'),
            types.InlineKeyboardButton('На доработку(+1 день)', callback_data=f'retry_rep_{id}'),
            row_width=2
        )
    markup.add(
        types.InlineKeyboardButton('Назад', callback_data=('completed_quests_0' if not back_to_all else 'all_quests_0'))
    )

    return markup

def stop_get_photos():
    markup = types.ReplyKeyboardMarkup()
    markup.add(
        types.KeyboardButton('Закончить отправку фото'),
        types.KeyboardButton('Назад'),
        row_width=1
    )

    return markup