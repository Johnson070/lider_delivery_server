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