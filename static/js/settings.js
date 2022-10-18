function download_db() {
    window.Telegram.WebApp.showAlert('Ожидайте');
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/download_db/'+document.getElementById('user_id').textContent, true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.Telegram.WebApp.showAlert('База данных была отправлена в чат.');
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function create_link() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/create_link/'+document.getElementById('user_id').textContent, true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.Telegram.WebApp.showAlert('Приглашение отправлено в чат.');
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function save_report_costs() {
    out_costs = {}

    let inputs = document.querySelectorAll('.text-info-container input');

    for (var i = 0; i < inputs.length; i++)
        out_costs[inputs[i].id.match(/(\d+)/)[0]] = parseFloat(inputs[i].value);


    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/costs', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(out_costs)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
            window.Telegram.WebApp.showAlert('Сохранено.');
        }
        else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function get_report_costs() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/costs', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                var div_costs = document.getElementById('reports-costs');

                Object.entries(JSON.parse(this.responseText)).forEach(([key, value]) => {
                   var container = document.createElement('div');
                   container.className = 'text-info-container';

                   var name = document.createElement('div');
                   name.className = 'name-property';
                   name.innerText = value[0];

                   var input_value = document.createElement('div');
                   input_value.className = 'value-property';
                   input_value.innerHTML = `<input id="cost_${key}" type="number" style="width: 80px;" value="${value[1]}" inputmode="decimal" required>`;

                   container.appendChild(name);
                   container.appendChild(input_value);
                   div_costs.appendChild(container);
                });
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function get_user_permissions() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/permissions', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                var div_costs = document.getElementById('user-permissions');

                Object.entries(JSON.parse(this.responseText)).forEach(([key, value]) => {
                   var container = document.createElement('div');
                   container.className = 'text-info-container';

                   var name = document.createElement('div');
                   name.className = 'name-property';
                   name.innerText = value[0];

                   var input_value = document.createElement('div');
                   input_value.className = 'value-property';
                   input_value.innerHTML = `<select style="width: 120px;" onchange="set_user_permission(this)">
                                                <option id="user_${key}" ${value[1] == 'user' ? 'selected' : ''}>Юзверь</option>
                                                <option id="admin_${key}" ${value[1] == 'admin' ? 'selected' : ''}>Админ</option>
                                                <option id="moder_${key}" ${value[1] == 'moder' ? 'selected' : ''}>Модератор</option>
                                            </select>`;

                   container.appendChild(name);
                   container.appendChild(input_value);
                   div_costs.appendChild(container);
                });
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function set_user_permission(elem) {
    var data = elem.options[elem.selectedIndex]

    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/permissions', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify([data.id.match(/(\d+)/)[0], data.id.match(/([a-z]+)/)[0]])); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
            window.Telegram.WebApp.showAlert('Сохранено.');
        }
        else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}