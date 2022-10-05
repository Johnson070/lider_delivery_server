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
                if (item.id == 'kick') window.location.href = '/users'
                document.location.reload(true)
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function change_balance(elem) {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href+'/balance', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(elem.value); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                document.location.reload(true)
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function get_routes() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', '/routes/list', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                json = JSON.parse(this.responseText)

                routes = document.getElementById('select-route')

                for (var i = 0; i < json.length; i++){
                    route = document.createElement('option')
                    route.innerText = json[i][1];
                    route.value = json[i][0];
                    routes.appendChild(route);
                }
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function add_mission(){
    let uuid_mission = document.getElementById("select-route").value;
    let name_mission = document.getElementById("name-mission").value;
    let days_expired = document.getElementById("days-expired").value;
    let reward = document.getElementById("reward").value;
    let count_reports = document.getElementById("count-reports").value;

    if (uuid_mission === '' || name_mission === '' || days_expired === '' || reward === '' || count_reports === '') {
        window.Telegram.WebApp.showAlert("Проверьте заполнены ли все поля");
        return;
    }

    json = {
        uuid: uuid_mission,
        name: name_mission,
        days: days_expired,
        reward: reward,
        reports: count_reports
    }

    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/add_mission', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(json)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.location.reload();
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}