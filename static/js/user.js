function get_missions() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href+'/missions', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                json = JSON.parse(this.responseText);
                missions = document.getElementById("missions");

                for (var i = 0; i < json.length; i++) {
                    item = document.createElement('li');
                    item.innerText = json[i];
                    missions.appendChild(item);
                }
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function manage_user() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href+'/'+item.id, true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                document.location.reload(true)
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}