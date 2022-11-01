import time
import bot_tg
import server_flask
import settings
import settings as st
import datetime

import threading

serve_on_server = False

def application(a=None,b=None):
    bot_tg.bot.remove_webhook()
    if serve_on_server:
        time.sleep(0.1)

        bot_tg.bot.set_webhook(url=st.WEBHOOK_URL_BASE + st.WEBHOOK_URL_PATH)
    else:
        st.WEBHOOK_URL_BASE = 'https://127.0.0.1/delivery_bot'

    while True:
        try:
            if serve_on_server:
                pass
            else:
                # threading.Thread(target=bot_tg.bot.polling).start()
                pass

            server_flask.application.run(debug=True, host='localhost', port=443, ssl_context=('localhost.crt', 'localhost.key'))
        except Exception as e:
            print(e)
            print('restart',  datetime.datetime.now())


if not serve_on_server:
    application()