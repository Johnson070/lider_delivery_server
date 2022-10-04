function get_routes() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', 'routes/list', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                if(this.responseText == '0') window.location.href = '/unauthorized'
                else {
                    json = JSON.parse(this.responseText)

                    routes = document.getElementById('routes')

                    for (var i = 0; i < json.length; i++){
                        route = document.createElement('a')
                        route.href = `/routes/${json[i][0]}`;
                        route.innerText = json[i][1];
                        route.className = 'button'
                        routes.appendChild(route)
                    }
                }
            }
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
                if(this.responseText == '0') window.location.href = '/unauthorized'
                else window.location.href = '/routes'
            }
        }
    };
}
