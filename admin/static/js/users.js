function users() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', '/delivery_bot/users/list', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                json = JSON.parse(this.responseText)

                users = document.getElementById('users')

                for (var i = 0; i < json.length; i++){
                    user = document.createElement('a')
                    user.href = `/delivery_bot/user/${json[i][0]}`;
                    user.innerText = json[i][1];
                    user.className = 'button'
                    users.appendChild(user)
                }
            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
        }
    };
}