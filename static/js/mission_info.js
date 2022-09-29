function add_coll_listener() {
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block" || content.style.display === "grid") {
                content.style.display = "none";
            } else {
                if (content.className.search('report') != -1) content.style.display = 'grid';
                else content.style.display = "block";
            }
        });
    }
}

var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', '/validate', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
            if(this.responseText == '0') window.location.href = '/unauthorized'
        }
    }
};

var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', window.location.href + '/report', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
            if(this.responseText == '0') window.location.href = '/unauthorized'
            else {
                json = JSON.parse(this.responseText);
                reports = document.getElementById("reports");

                for (var i = 0; i < json.length; i++) {
                    item = document.createElement('button');
                    item.type = 'button';
                    item.className = 'collapsible';
                    item.innerText = 'Отчет ' + (i+1);
                    reports.appendChild(item);

                    report = document.createElement('div');
                    report.className = 'report-grid';

                    images = document.createElement('div');
                    images.className = 'report-grid-photos'
                    for (var j = 0; j < json[i]['photos'].length; j++) {
                        photo = document.createElement('img');
                        photo.className = 'report-grid-photo';
                        photo.src = `/get_file?file_id=${json[i]['photos'][j]}`;
                        images.appendChild(photo);
                    }
                    report.appendChild(images)

                    video = document.createElement('iframe');
                    video.src = `/get_file?file_id=${json[i]['video']}`;
                    report.appendChild(video);

                    reports.appendChild(report)
                }

                add_coll_listener()
            }
        }
    }
};

add_coll_listener()
let tg = window.Telegram.WebApp

tg.expand(); //расширяем на все окно

function manage_mission(item) {
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