function get_missions() {
      var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
      xmlhttp.open('GET', window.location.href+'/missions', true); // Открываем асинхронное соединение
      xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
      xmlhttp.send(); // Отправляем POST-запрос
      xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
      if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
          if(this.responseText == '0') window.location.href = '/unauthorized';
          else {
             json = JSON.parse(this.responseText);
             missions = document.getElementById("missions");

             for (var i = 0; i < json.length; i++) {
                item = document.createElement('li');
                item.innerText = json[i];
                missions.appendChild(item);
             }
          }
        }
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
           if(this.responseText == '0') window.location.href = '/unauthorized'
           else document.location.reload(true)
        }
     }
  };
}