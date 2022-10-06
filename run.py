import time
import bot_tg as bot_sv
import server_flask as fls_sv
import settings as st
import datetime

import threading

serve_on_server = False

def application(a=None,b=None):
    bot_sv.bot.remove_webhook()
    if serve_on_server:
        time.sleep(0.1)

        bot_sv.bot.set_webhook(url=st.WEBHOOK_URL_BASE + st.WEBHOOK_URL_PATH)

    while True:
        try:
            bot_sv.start_bot()

            if serve_on_server:
                pass
            else:
                 threading.Thread(target=bot_sv.bot.polling).start()

            fls_sv.start_server(serve_on_server)
        except Exception as e:
            print(e)
            print('restart',  datetime.datetime.now())

if not serve_on_server:
    application()