var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', '/delivery_bot/user/validate', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)

        }
        else window.location.href = '/delivery_bot/unauthorized'
    }
};

function get_missions() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', '/delivery_bot/user/get_missions', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                let buttons = document.getElementById('main');

                let json = JSON.parse(this.responseText);

                for (var i = 0; i < json.length; i++) {
                    item = document.createElement('a');
                    item.href = `/delivery_bot/user/mission/${json[i][0]}`;
                    item.innerText = json[i][1];
                    item.className = 'button'
                    buttons.appendChild(item);
                }
            }
            else window.location.href = '/delivery_bot/unauthorized'
        }
    };
}