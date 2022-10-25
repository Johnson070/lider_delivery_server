function get_routes() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', 'routes/list', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                json = JSON.parse(this.responseText)

                routes = document.getElementById('routes')

                for (var i = 0; i < json.length; i++){
                    route = document.createElement('a')
                    route.href = `/delivery_bot/routes/${json[i][0]}`;
                    route.innerText = json[i][1];
                    route.className = 'button'
                    routes.appendChild(route)
                }
            }
            else if (xmlhttp.status == 401) window.location.href = '/delivery_bot/unauthorized';
        }
    };
}

function delete_route() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/delete', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.location.href = '/delivery_bot/routes'
            }
            else if (xmlhttp.status == 401) window.location.href = '/delivery_bot/unauthorized';
        }
    };
}

async function save_route() {
    let file = document.getElementById('file-route').files[0];
    let file1 = document.getElementById('photo').files[0];
    let link_map = document.getElementById("link-map").value;
    let name_route = document.getElementById("name-route").value;

    if (file === undefined || file1 === undefined || link_map.match(/https:\/\/yandex\.ru\/maps\/\?um=constructor(.+)/) == null || name_route === '') {
        window.Telegram.WebApp.showAlert('Заполните все поля и выберите файлы!');
        return;
    }

    photo = await file1.arrayBuffer()
    geojson = await file.text()

    photo = Array.from(new Uint8Array(photo))

    json = {
        photo_bytes: photo,
        geojson: geojson,
        link_map: link_map,
        name_route: name_route
    }

    window.Telegram.WebApp.showAlert('Ожидайте');
    document.getElementById('route-add-popup').style.display = 'none';
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/add', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(json)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                if (this.responseText == '-1') {
                    window.Telegram.WebApp.showAlert('Произошла ошибка при добавлении. Проверьте файлы!');
                    return;
                }

                window.location.reload(true);
            }
            else if (xmlhttp.status == 401) window.location.href = '/delivery_bot/unauthorized';
        }
    };
}
