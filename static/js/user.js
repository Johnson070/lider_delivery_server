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
                remove_buttons = document.getElementById('remove-missions');

                for (var i = 0; i < json.length; i++) {
                    item = document.createElement('li');
                    link_mission = document.createElement('a');
                    link_mission.className = 'link_user';
                    link_mission.innerText = json[i][1];
                    link_mission.href = `/mission/${json[i][0]}`;
                    item.appendChild(link_mission);
                    missions.appendChild(item);

                    btn = document.createElement('button');
                    btn.className = 'button';
                    btn.innerText = json[i][1];
                    btn.id = json[i][0];

                    const id = json[i][0];
                    btn.onclick = function () {
                        window.Telegram.WebApp.showConfirm('Вы уверены что хотите удалить миссию у пользователя?',
                            function (state) {
                                if (state) delete_mission(id);
                            });
                    }
                    remove_buttons.appendChild(btn);
                }
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function kick_user_confirm() {
    window.Telegram.WebApp.showConfirm('Вы уверены что хотите исключить пользователя?', function (state) {
        if (state) kick_user();
    })
}

function kick_user() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href+'/kick', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.location.href = '/users'
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function confirm_pass_balance() {
    window.Telegram.WebApp.showConfirm('Вы уверены что хотите списать баланс пользователя?',
        function (state) {
            if (state) change_balance();
        })
}

function change_balance(elem = null) {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href+'/balance', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(elem != null ? elem.value : 0); // Отправляем POST-запрос
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
                    route.setAttribute('id', json[i][2]);
                    route.value = json[i][0];
                    routes.appendChild(route);

                    if (i == 0) document.getElementById('count-reports').value = json[0][2];
                }
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function changeFunc() {

}

function change_reports() {
    var selectBox = document.getElementById("select-route");
    var selectedValue = selectBox.options[selectBox.selectedIndex].id;
    document.getElementById('count-reports').value = selectedValue;
}

function add_mission(){
    let uuid_mission = document.getElementById("select-route").value;
    let name_mission = document.getElementById("name-mission").value;
    let days_expired = document.getElementById("days-expired").value;
    // let reward = document.getElementById("reward").value;
    let count_reports = document.getElementById("count-reports").value;

    if (uuid_mission === '' || name_mission === '' || days_expired === '' || count_reports === '') {
        window.Telegram.WebApp.showAlert("Проверьте заполнены ли все поля");
        return;
    }

    json = {
        uuid: uuid_mission,
        name: name_mission,
        days: days_expired,
        reward: 0,
        reports: count_reports
    }

    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/add_mission', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(json)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status != 401) { // Сервер вернул код 200 (что хорошо)
                window.location.reload();
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function delete_mission(id) {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/delete_mission', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(id); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.location.reload();
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}