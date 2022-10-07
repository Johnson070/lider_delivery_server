// TODO: сделать динамическую прогрузку фото

var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', '/validate', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if (xmlhttp.status == 401) window.location.href = '/unauthorized';
    }
};

var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', window.location.href + '/report', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
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
                    photo.loading = 'lazy';
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
        else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
    }
};

let tg = window.Telegram.WebApp

tg.expand(); //расширяем на все окно

function manage_mission(item) {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href+'/'+item.id, true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                document.location.reload(true)
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}