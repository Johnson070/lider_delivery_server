import datetime
import re
import uuid

import jsonpickle

from bot_tg import bot
import telebot
import settings as sett
import functions as func
import markups
from telebot import types

bot: telebot.TeleBot
bot = bot


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
        # print('Delete chat for user: ', call.message.chat.username)
        # # for i in range(0, msg_last.message_id):  # удаление прошлых сообщений в чате()
        # #     try:
        # #         bot.delete_message(call.message.chat.id, i, timeout=500)
        # #     except:
        # #         pass


def parse_photos_report(msg: types.Message, coords, id, building_id, type_rep, group_id=None):
    if msg.content_type == 'photo':
        bot.delete_message(msg.chat.id, msg.message_id)

        if not func.check_file_hash(msg.photo[-1].file_unique_id):
            try:
                bot.edit_message_text('Для каждого отчета нужно отправлять новые фотографии!\n'
                                      'Отправьте фотоотчёт отправка БЕЗ СЖАТИЯ!',
                                      msg.chat.id,
                                      msg.message_id,
                                      reply_markup=markups.end_send_media('end_photo_send'))
            except:
                pass
            bot.register_next_step_handler(msg, parse_photos_report, coords, id, building_id, type_rep, group_id)
            return

        if group_id is None:
            group_id = str(uuid.uuid4())

        func.add_photo_to_media(group_id, msg.photo[-1].file_id, msg.photo[-1].file_unique_id)

        bot.register_next_step_handler(msg, parse_photos_report, coords, id, building_id, type_rep, group_id)
    else:
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass
        bot.register_next_step_handler(msg, parse_photos_report, coords, id, building_id, type_rep, group_id)


def parse_video(msg: types.Message, start_msg_id, coords, id, building_id, type_rep, photos):
    if msg.content_type == 'text' and msg.text == '/start':
        func.delete_media_by_group_id(photos)
        handler_start(msg)
    elif msg.content_type == 'video_note':
        video_file_id = str(msg.video_note.file_id)

        func.save_report_user(id, msg.chat.id, coords, photos, video_file_id, building_id, type_rep)
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.delete_message(msg.chat.id, start_msg_id)
        except:
            pass
        bot.send_message(msg.chat.id,
                         'Отчет сохранён.',
                         reply_markup=types.InlineKeyboardMarkup().add(
                             types.InlineKeyboardButton('Вернуться', callback_data=f'building_{building_id}_{id}')))
    else:
        try:
            bot.delete_message(msg.chat.id, msg.message_id)
        except:
            pass
        bot.register_next_step_handler(msg, parse_video, start_msg_id, coords, id, photos, type_rep)
        return


# # =========================
# # Информация о трудящимся(не админ)
# # =========================
# @bot.callback_query_handler(lambda call: call.data == 'information')
# def user_info_clerk(call: types.CallbackQuery):
#     bot.clear_step_handler_by_chat_id(call.message.chat.id)  # очистить очередь хандлеров если был выход
#
#     id = call.message.chat.id
#     clerk = func.get_clerk_by_id(id)
#     missions = [i[1] for i in func.get_missions_by_user_id(id)]
#
#     try:
#         bot.edit_message_text(sett.info_user_text.format(
#             clerk[1], clerk[2], clerk[3], '\n'.join(missions) if missions else '<b>Нет заданий</b>'),
#             call.message.chat.id,
#             call.message.message_id,
#             parse_mode='HTML',
#             reply_markup=markups.back_cleck_menu())
#     except:
#         bot.send_message(call.message.chat.id, sett.info_user_text.format(
#             clerk[1], clerk[2], clerk[3], '\n'.join(missions) if missions else '<b>Нет заданий</b>'),
#                          parse_mode='HTML',
#                          reply_markup=markups.back_cleck_menu())
#     # except:
#     #     pass
#
# # =========================
# # Завершить задание
# # =========================
# @bot.callback_query_handler(lambda call:
#                             re.search(r'^confirm_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def confirm_complete_mission(call: types.CallbackQuery):
#     id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#     bot.send_message(call.message.chat.id,
#                      'Вы уверены что хотите завершить задание?',
#                      reply_markup=markups.confirm_end_mission(id))
#
# @bot.callback_query_handler(lambda call:
#                             re.search(r'^complete_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def complete_mission(call: types.CallbackQuery):
#     id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#     func.complete_mission(id)
#     show_mission_user(call)
#
# # =========================
# # Добавить отчет к заданию
# # =========================
# @bot.callback_query_handler(
#     lambda call: re.search(r'^report_mission_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def add_report_mission(call: types.CallbackQuery):
#     id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#     reports = func.get_count_reports_mission(id, 0)
#     route_id = func.get_full_info_mission(id)[3]
#     location = func.get_coords_mission_by_id(route_id)
#     count_buildings = func.get_route_buildings(route_id)
#
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#     except:
#         pass
#
#     bot.send_location(call.message.chat.id,
#                       location[str(0)][0],
#                       location[str(0)][1],
#                       live_period=86400,
#                       heading=1,
#                       proximity_alert_radius=1)
#     bot.send_message(call.message.chat.id,
#                      f'Текущий дом: {0 + 1}\n'
#                      f'Кол-во отчетов: {reports}',
#                      reply_markup=markups.select_user_building(0, id, count_buildings))
#
# @bot.callback_query_handler(
#     lambda call: re.search(r'building_(\d+)_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def change_building(call: types.CallbackQuery):
#     id_building = re.search(r'(\d+)', call.data).group(0)
#     id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#     reports = func.get_count_reports_mission(id, id_building)
#     route_id = func.get_full_info_mission(id)[3]
#     location = func.get_coords_mission_by_id(route_id)
#     count_buildings = func.get_route_buildings(route_id)
#
#     try:
#         bot.edit_message_live_location(location[id_building][0],
#                                        location[id_building][1],
#                                        call.message.chat.id,
#                                        call.message.message_id - 1,
#                                        timeout=40)
#
#         bot.edit_message_text(f'Текущий дом: {int(id_building) + 1}\n'
#                               f'Кол-во отчетов: {reports}',
#                               call.message.chat.id,
#                               call.message.message_id,
#                               reply_markup=markups.select_user_building(int(id_building), id, count_buildings))
#     except Exception as e:
#         print(e)
#         try:
#             bot.delete_message(call.message.chat.id, call.message.message_id - 1)
#         except:
#             pass
#         try:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#         except:
#             pass
#
#         bot.send_location(call.message.chat.id,
#                           location[id_building][0],
#                           location[id_building][1],
#                           live_period=86400,
#                           heading=1,
#                           timeout=40,
#                           proximity_alert_radius=1)
#         bot.send_message(call.message.chat.id,
#                          f'Текущий дом: {int(id_building) + 1}\n'
#                          f'Кол-во отчетов: {reports}',
#                          reply_markup=markups.select_user_building(int(id_building), id, count_buildings))
#
# @bot.callback_query_handler(
#     lambda call: re.search(r'^select_type_(\d+)_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def select_report_type(call: types.CallbackQuery):
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#     except:
#         pass
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id - 1)
#     except:
#         pass
#
#     id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#     building_id = re.search(r'(\d+)', call.data).group(0)
#     bot.send_message(call.message.chat.id,
#                      'Выберите тип отчета',
#                      reply_markup=types.InlineKeyboardMarkup().add(
#                          *[types.InlineKeyboardButton(func.get_costs()[i][0],
#                                                       callback_data=f'ent_report_{i}_{building_id}_{id}') for i in
#                            func.get_costs().keys()],
#                          types.InlineKeyboardButton("Назад", callback_data=f'building_{building_id}_{id}'),
#                          row_width=1
#                      ))
#
# @bot.callback_query_handler(
#     lambda call: re.search(r'ent_report_(\d+)_(\d+)_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def start_add_report(call: types.CallbackQuery):
#     id = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#     type_rep = re.findall(r'(\d+)', call.data)[0]
#     building_id = re.findall(r'(\d+)', call.data)[1]
#     msg = bot.send_message(call.message.chat.id,
#                            'Не уходите с места где вы размещали рекламу.\n\n'
#                            'Отправьте свою геолокацию',
#                            reply_markup=markups.get_location_menu())
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#     except:
#         pass
#
#     bot.register_next_step_handler(msg, check_location, msg.message_id, id, building_id, type_rep)
#
#
# def check_location(msg: types.Message, start_msg_id, id, building_id, type_rep):
#     if msg.content_type == 'text' and (msg.text == '/start' or msg.text == 'Назад'):
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#             bot.delete_message(msg.chat.id, start_msg_id)
#         except:
#             pass
#         handler_start(msg)
#     elif msg.content_type != 'web_app_data':  # and msg.content_type != 'location': #T#ODO: удалить
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#         except:
#             pass
#         bot.register_next_step_handler(msg, check_location, start_msg_id, id, building_id, type_rep)
#         return
#     try:
#         location = jsonpickle.decode(msg.web_app_data.data)
#         # location = jsonpickle.decode(msg.web_app_data.data) if msg.content_type == 'web_app_data' \
#         #     else {'latitude':msg.location.latitude, 'longitude':msg.location.longitude}
#
#         pass_location = func.check_coordinates(id, location['latitude'], location['longitude'])
#         if pass_location == 1:
#             bot.delete_message(msg.chat.id, msg.message_id)
#
#             try:
#                 bot.delete_message(msg.chat.id, start_msg_id)
#             except:
#                 pass
#
#             start_msg_id = bot.send_message(msg.chat.id,
#                                             'Не уходите с места где вы размещали рекламу.\n'
#                                             'Если вы уйдете далеко от точки, то геолокация не зачтется.\n\n'
#                                             'Отправьте свою геолокацию',
#                                             reply_markup=markups.get_location_menu()).message_id
#
#             bot.register_next_step_handler(msg, check_location, start_msg_id, id, building_id, type_rep)
#             return
#         elif pass_location == 2:
#             bot.delete_message(msg.chat.id, msg.message_id)
#             try:
#                 bot.delete_message(msg.chat.id, start_msg_id)
#             except:
#                 pass
#
#             for admin_chat_id in func.get_admins():
#                 bot.send_message(admin_chat_id,
#                                  f'Система обнаружила, что пользователь {msg.chat.username} перемещяется слишком быстро.\n'
#                                  f'Задание: {func.get_full_info_mission(id)[2]}')
#
#             bot.send_message(msg.chat.id,
#                              'Кажется вы перемещяетесь слишком быстро.\n'
#                              'За повторное нарушение вам будет начислен штраф!',
#                              reply_markup=markups.back_cleck_menu())
#
#             return
#
#         coords = (location['latitude'], location['longitude'])
#         bot.delete_message(msg.chat.id, msg.message_id)
#         bot.delete_message(msg.chat.id, start_msg_id)
#         msg_new = bot.send_message(msg.chat.id,
#                                    'Отправьте фотоотчёт отправка БЕЗ СЖАТИЯ!',
#                                    reply_markup=markups.stop_get_photos())
#         bot.register_next_step_handler(msg_new, parse_photos_report, msg_new.message_id, coords, id, building_id,
#                                        type_rep, None)
#     except:
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#         except:
#             pass
#         bot.register_next_step_handler(msg, check_location, start_msg_id, id, building_id, type_rep)
#         return
#
# def parse_photos_report(msg: types.Message, start_msg_id, coords, id, building_id, type_rep, group_id):
#     if msg.content_type == 'text' and (msg.text == '/start' or msg.text == 'Назад'):
#         func.delete_media_by_group_id(group_id)
#         handler_start(msg)
#     elif group_id is not None and msg.text == 'Закончить отправку фото':
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#             bot.delete_message(msg.chat.id, start_msg_id)
#         except:
#             pass
#         new_msg = bot.send_message(msg.chat.id,
#                                    'Отправьте кружочек с окружением и флаерами.',
#                                    reply_markup=types.ReplyKeyboardRemove())
#         bot.register_next_step_handler(new_msg, parse_video, new_msg.message_id, coords, id, building_id, type_rep,
#                                        group_id)
#         return
#     elif msg.content_type == 'photo':
#         bot.delete_message(msg.chat.id, msg.message_id)
#
#         if not func.check_file_hash(msg.photo[-1].file_unique_id):
#             try:
#                 bot.delete_message(msg.chat.id, start_msg_id)
#             except:
#                 pass
#
#             start_msg_id = bot.send_message(msg.chat.id,
#                                             'Для каждого отчета нужно отправлять новые фотографии!\n'
#                                             'Отправьте фотоотчёт отправка БЕЗ СЖАТИЯ!',
#                                             reply_markup=markups.stop_get_photos()).message_id
#             bot.register_next_step_handler(msg, parse_photos_report, start_msg_id, coords, id, building_id,
#                                            type_rep, group_id)
#             return
#
#         if group_id is None:
#             group_id = str(uuid.uuid4())
#
#         func.add_photo_to_media(group_id, msg.photo[-1].file_id, msg.photo[-1].file_unique_id)
#
#         bot.register_next_step_handler(msg, parse_photos_report, start_msg_id, coords, id, building_id, type_rep,
#                                        group_id)
#     else:
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#         except:
#             pass
#         bot.register_next_step_handler(msg, parse_photos_report, start_msg_id, coords, id, building_id, type_rep,
#                                        group_id)
#
# def parse_video(msg: types.Message, start_msg_id, coords, id, building_id, type_rep, photos):
#     if msg.content_type == 'text' and msg.text == '/start':
#         func.delete_media_by_group_id(photos)
#         handler_start(msg)
#     elif msg.content_type == 'video_note':
#         video_file_id = str(msg.video_note.file_id)
#
#         func.save_report_user(id, msg.chat.id, coords, photos, video_file_id, building_id, type_rep)
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#             bot.delete_message(msg.chat.id, start_msg_id)
#         except:
#             pass
#         bot.send_message(msg.chat.id,
#                          'Отчет сохранён.',
#                          reply_markup=types.InlineKeyboardMarkup().add(
#                              types.InlineKeyboardButton('Вернуться', callback_data=f'building_{building_id}_{id}')))
#     else:
#         try:
#             bot.delete_message(msg.chat.id, msg.message_id)
#         except:
#             pass
#         bot.register_next_step_handler(msg, parse_video, start_msg_id, coords, id, photos, type_rep)
#         return
#
# # =========================
# # обработчики отчетов пользователя по маршрутам
# # =========================
# # =========================
# # Задания промоутера
# # =========================
# @bot.callback_query_handler(lambda call: call.data == 'quests_user')
# def get_missions_user(call: types.CallbackQuery):
#     try:
#         bot.edit_message_text('Текущие задания.',
#                               call.message.chat.id,
#                               call.message.message_id,
#                               reply_markup=markups.missions_by_user_id_menu(call.message.chat.id))
#     except:
#         bot.send_message(call.message.chat.id, 'Ошибка!')
#
# @bot.callback_query_handler(
#     lambda call: re.search(r'quests_user_back_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data) is not None)
# def get_missions_user(call: types.CallbackQuery):
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id - 1)
#     except:
#         pass
#     try:
#         show_mission_user(call)
#     except:
#         bot.send_message(call.message.chat.id, 'Ошибка!')
#
# @bot.callback_query_handler(lambda call: re.search(r'quest_user_(([a-f0-9]+-){4}([a-f0-9]+))$', call.data))
# def show_mission_user(call: types.CallbackQuery):
#     id_mission = re.search(r'(([a-f0-9]+-){4}([a-f0-9]+))$', call.data).group(0)
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#     except:
#         pass
#
#     mission = func.get_full_info_mission(id_mission)
#
#     if mission is None:
#         bot.send_message(call.message.chat.id, 'Такого задания не существует!')
#         return
#
#     route = func.get_route(mission[3])
#     pic_file = route[4]
#     link_route = route[2]
#     count_reports = func.get_count_reports_mission(id_mission)
#     expired = True if datetime.datetime.strptime(mission[4],
#                                                  '%Y-%m-%d %H:%M:%S') < datetime.datetime.now() else False
#     expired = True if mission[7] == 1 else expired
#
#     time_todo = datetime.datetime.strptime(mission[4], "%Y-%m-%d %H:%M:%S") - datetime.datetime.now()
#
#     bot.send_photo(call.message.chat.id,
#                    pic_file,
#                    caption='Это область в которой вы должны распространить рекламу.\n\n'
#                            + ("<u><b>Время для выполнения задания закончилось</b></u>\n" if expired else "") +
#                            f'Комментарий: {mission[2]}\n\n'
#                            f'Кол-во домов: {mission[5]}\n'
#                            f'Заработано: {mission[6]} р.\n\n'
#                            f'Сделано <b>{count_reports}</b>\n\n'
#                            f'{"" if expired else f"У вас осталось: {time_todo.days} дн(ь/я/ей) {time_todo.seconds // 60 % 60} час(a/ов) {time_todo.seconds % 60} минут"}'
#                            f'\nМаршрут: <a href="{link_route}">открыть</a>',
#                    parse_mode='HTML',
#                    reply_markup=markups.mission_menu(mission[0], expired, link_route),
#                    protect_content=True)

def init_user_actions():
    print('start user actions')


if __name__ == '__main__':
    init_user_actions()
