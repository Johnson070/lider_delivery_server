# Бот для отслеживания распространения флаеров
# by Johnson070(Vladimir Veber)
# https://github.com/johnson070
# https://t.me/vveber

# создано для "Лидер сервис"
import datetime
import logging
import re, os
import telebot
from telebot import types

import settings as sett

bot = telebot.TeleBot(sett.API_KEY, threaded=False)  # реализация
telebot.logger.setLevel(logging.DEBUG)

import functions as func
import report_zip
import markups

# фильтр для проверки на права администратора
class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_chat_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        return (message.from_user.id in sett.admins)


class IsAdminCallback(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_callback_admin'

    @staticmethod
    def check(call: telebot.types.CallbackQuery):
        return (call.message.chat.id in sett.admins)


bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(IsAdminCallback())


def start_bot():
    global bot

    @bot.message_handler(commands=['start'])
    def handler_start(msg):
        args = msg.text.split(' ')
        bot.clear_step_handler_by_chat_id(msg.chat.id)
        if len(args) > 1:
            if func.check_user_in_database(msg.chat.id, msg.chat.username):  # проверка что пользователь в базе
                bot.send_message(msg.chat.id, 'Вы уже использовали приглашение',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(msg.chat.id, 'Бот-помощник для контроля раздачи листовок',
                                 reply_markup=markups.get_clerk_menu())
            elif func.use_invite_link(args[1], msg.chat.id, msg.chat.username):  # проверка кода приглашения
                bot.send_message(msg.chat.id, 'Ваше приглашение использовано.',
                                 reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(msg.chat.id, 'Бот-помощник для контроля раздачи листовок',
                                 reply_markup=markups.get_clerk_menu())
            else:
                bot.send_message(msg.chat.id, 'Недествительное приглашение!', reply_markup=types.ReplyKeyboardRemove())
        elif func.check_user_in_database(msg.chat.id, msg.chat.username):
            bot.send_message(msg.chat.id, 'Начало работы!', reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(msg.chat.id, 'Бот-помощник для контроля раздачи листовок',
                             reply_markup=markups.get_clerk_menu())
        else:
            msg_last = bot.send_message(msg.chat.id, 'Получите ссылку на приглашения у администратора.')
            # for i in range(0, msg_last.message_id):  # удаление прошлых сообщений в чате()
            #     try:
            #         bot.delete_message(msg.chat.id, i, timeout=1)
            #     except:
            #         pass

    @bot.message_handler(commands=['admin', 'admin_full'], is_chat_admin=True)
    def admin_menu(msg):
        full = msg.text == '/admin_full'
        bot.clear_step_handler_by_chat_id(msg.chat.id)
        bot.send_message(msg.chat.id, 'Админ панель', reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(msg.chat.id, 'Здесь вы можете настроить маршруты, задания, выдать пригласительный код.',
                         reply_markup=markups.get_admin_menu(full))

    # # Канал куда будут пересылаться сообщения с media_group_id
    # @bot.channel_post_handler(commands=['start'])
    # def handler_start(msg):
    #     func.set_channel_photo_sklad(msg.chat.id)
    #     bot.send_message(msg.chat.id, "Канал установлен для отправки и хранения фотографий отчетов.")

    @bot.callback_query_handler(lambda call: call.data == 'start' or call.data == 'start_del')
    def start_handler(call: types.CallbackQuery):
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        if call.data == 'start_del':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            call.message = bot.send_message(call.message.chat.id, 'Начало работы')
        if func.check_user_in_database(call.message.chat.id, call.message.chat.username):
            bot.edit_message_text('Бот-помощник для контроля раздачи листовок',
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=markups.get_clerk_menu())
        else:
            msg_last = bot.edit_message_text('Получите ссылку на приглашения у администратора.',
                                             call.message.chat.id,
                                             call.message.message_id)
            print('Delete chat for user: ', call.message.chat.username)
            for i in range(0, msg_last.message_id):  # удаление прошлых сообщений в чате()
                try:
                    bot.delete_message(call.message.chat.id, i, timeout=500)
                except:
                    pass

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
        bot.delete_message(call.message.chat.id, call.message.message_id)
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
    @bot.callback_query_handler(lambda call: call.data == 'invite_link', is_callback_admin=True)
    def create_invite_link(call: types.CallbackQuery):
        link, image = func.create_invite_link(call.message.chat.username)
        bot.send_photo(call.message.chat.id, image,
                       parse_mode='HTML',
                       caption=f'Приглашение активно 6 часов после создания.\n'
                               f'<a href="{link}">Активировать</a>')

    # =========================
    # Вернуться в админ панель
    # =========================
    @bot.callback_query_handler(lambda call: call.data == 'back_admin', is_callback_admin=True)
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
        try:
            bot.edit_message_text(sett.info_user_text.format(
                clerk[1], clerk[2], clerk[3], '\n'.join(missions) if missions else '<b>Нет заданий</b>'),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=markups.get_clerk_control_menu(clerk[0]))
        finally:
            pass

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

        bot.edit_message_text('Введите новый баланс',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=markups.back_to_clerk_menu(id))
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
    # обработчики отчетов пользователя по маршрутам
    # =========================
    # =========================
    # Задания промоутера
    # =========================
    @bot.callback_query_handler(lambda call: call.data == 'quests_user')
    def get_missions_user(call: types.CallbackQuery):
        bot.edit_message_text('Текущие задания.',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=markups.missions_by_user_id_menu(call.message.chat.id))

    @bot.callback_query_handler(lambda call: re.search(r'quest_user_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data))
    def show_mission_user(call: types.CallbackQuery):
        id_mission = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        mission = func.get_full_info_mission(id_mission)
        route = func.get_route(mission[3])
        pic_file = route[4]
        link_route = route[2]
        count_reports = func.get_count_reports_mission(id_mission)
        expired = True if datetime.datetime.strptime(mission[4],
                                                     '%Y-%m-%d %H:%M:%S') < datetime.datetime.now() else False
        expired = True if mission[7] == 1 else expired

        time_todo = datetime.datetime.strptime(mission[4], "%Y-%m-%d %H:%M:%S") - datetime.datetime.now()

        bot.send_photo(call.message.chat.id,
                       pic_file,
                       caption='Это область в которой вы должны распространить рекламу.\n\n'
                               + ("<u><b>Время для выполнения задания закончилось</b></u>\n" if expired else "") +
                               f'Комментарий: {mission[2]}\n\n'
                               f'Кол-во отчетов: {mission[5]}\n'
                               f'Стоимость: {mission[6]} р.\n\n'
                               f'Сделано <b>{count_reports}</b> из <b>{mission[5]}</b>\n\n'
                               f'{"" if expired else f"У вас осталось: {time_todo.days} дн(ь/я/ей) {time_todo.seconds // 60 % 60} час(a/ов) {time_todo.seconds % 60} минут"}'
                               f'\nМаршрут: <a href="{link_route}">открыть</a>',
                       parse_mode='HTML',
                       reply_markup=markups.mission_menu(mission[0], expired, link_route),
                       protect_content=True)

    # =========================
    # Добавить отчет к заданию
    # =========================
    @bot.callback_query_handler(
        lambda call: re.search(r'^report_mission_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
    def add_report_mission(call: types.CallbackQuery):
        id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
        msg = bot.send_message(call.message.chat.id,
                               'Отправьте свою геолокацию',
                               reply_markup=markups.get_location_menu())
        bot.delete_message(call.message.chat.id,
                           call.message.message_id)
        bot.register_next_step_handler(msg, check_location, msg.message_id, id)

    def check_location(msg: types.Message, start_msg_id, id):
        if msg.content_type == 'text' and msg.text == '/start':
            handler_start(msg)
        elif msg.content_type != 'location':
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.register_next_step_handler(msg, check_location, start_msg_id, id)
            return

        try:
            if not func.check_coordinates(id, msg.location.longitude, msg.location.latitude):
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.register_next_step_handler(msg, check_location, start_msg_id, id)
                return

            coords = (msg.location.longitude, msg.location.latitude)
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, start_msg_id)
            msg_new = bot.send_message(msg.chat.id,
                                       'Отправьте фотоотчёт до 10-ти фотографий в альбоме БЕЗ СЖАТИЯ!',
                                       reply_markup=types.ReplyKeyboardRemove())
            # bot.register_next_step_handler(msg_new, parse_photos_report, msg_new.message_id, coords, id)
            bot.register_next_step_handler(msg_new, parse_photos_report, msg_new.message_id, coords, id)
        except:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.register_next_step_handler(msg, check_location, start_msg_id, id)
            return

    # TODO: поменять алгоритм получения фото
    def parse_photos_report(msg: types.Message, start_msg_id, coords, id):
        if msg.content_type == 'text' and msg.text == '/start':
            handler_start(msg)
        elif msg.content_type == 'photo':
            files = None
            if msg.media_group_id is not None:
                bot.delete_message(msg.chat.id, start_msg_id)
                end_message_id = bot.send_message(msg.chat.id,
                                                  "Ожидайте",
                                                  reply_markup=types.ReplyKeyboardRemove()).message_id

                func.add_photo_to_media(msg.media_group_id, msg.photo[-1].file_id)
                files = msg.media_group_id

                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, end_message_id)
            else:
                files = msg.photo[-1].file_id
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.delete_message(msg.chat.id, start_msg_id)

            new_msg = bot.send_message(msg.chat.id,
                                       'Отправьте кружочек с окружением и флаерами.')
            bot.register_next_step_handler(new_msg, parse_video, new_msg.message_id, coords, id, files)
        else:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.register_next_step_handler(msg, parse_photos_report, start_msg_id, coords, id)

    def parse_video(msg: types.Message, start_msg_id, coords, id, photos):
        if msg.content_type == 'text' and msg.text == '/start':
            handler_start(msg)
        elif msg.content_type == 'video_note':
            video_file_id = str(msg.video_note.file_id)

            func.save_report_user(id, msg.chat.username, coords, photos, video_file_id)
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, start_msg_id)
            bot.send_message(msg.chat.id,
                             'Отчет сохранён.',
                             reply_markup=types.InlineKeyboardMarkup().add(
                                 types.InlineKeyboardButton('Вернуться', callback_data=f'quest_user_{id}')))
        else:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.register_next_step_handler(msg, parse_photos_report, start_msg_id, coords, id)
            return

    # =========================
    # Завершить задание
    # =========================
    @bot.callback_query_handler(lambda call:
                                re.search(r'^complete_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
    def complete_mission(call: types.CallbackQuery):
        id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
        func.complete_mission(id)
        show_mission_user(call)

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
        for i in range(msg_last.message_id-1, msg_last.message_id-200, -1):  # удаление прошлых сообщений в чате()
            try:
                bot.delete_message(id, i, timeout=0)
            except:
                pass

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
    @bot.callback_query_handler(lambda call: re.search(r'reset_links', call.data) is not None,
                                is_callback_admin=True)
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
                                 re.match(r'^mission_report_(([a-f0-9]+-){4}([a-f0-9]+))_#', call.data) is not None))

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
        file_name = report_zip.get_report(id)

        with open(file_name, 'rb') as zip:
            bot.send_document(call.message.chat.id, zip.read(),visible_file_name=f'report_mission_{datetime.datetime.now()}.zip')
        os.remove(file_name)
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

    # =========================
    # Информация о трудящимся(не админ)
    # =========================
    @bot.callback_query_handler(lambda call: call.data == 'information')
    def user_info_clerk(call: types.CallbackQuery):
        bot.clear_step_handler_by_chat_id(call.message.chat.id)  # очистить очередь хандлеров если был выход

        id = call.message.chat.id
        clerk = func.get_clerk_by_id(id)
        missions = [i[1] for i in func.get_missions_by_user_id(id)]

        bot.edit_message_text(sett.info_user_text.format(
            clerk[1], clerk[2], clerk[3], '\n'.join(missions) if missions else '<b>Нет заданий</b>'),
                              call.message.chat.id,
                              call.message.message_id,
                              parse_mode='HTML',
                              reply_markup=markups.back_cleck_menu())

    # @bot.message_handler(content_types=['photo'], func=lambda msg: msg.media_group_id is not None)
    # def save_media_group_id_photo(msg: types.Message):
    #     func.add_photo_to_media(msg.media_group_id, msg.photo[-1].file_id)
    #     bot.delete_message(msg.chat.id, msg.message_id)


if not __name__ == '__main__':
    start_bot()
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
