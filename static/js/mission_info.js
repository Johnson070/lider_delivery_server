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
                if (item.id == 'delete') window.location.href = '/'
                else document.location.reload(true)
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function confirm_delete_mission() {
    class item {
        constructor(id) {
            this.id = id
        }
    }

    const id = new item('delete')

    window.Telegram.WebApp.showConfirm('Вы уверены что хотите безвозратно удалить миссию? ',
    function (state) {
            if (state) manage_mission(id);
        });
}

function get_users(username) {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', '/users/list', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                users_list = JSON.parse(this.responseText)
                users_select = document.getElementById('select-user')

                for (var i = 0; i < users_list.length; i++) {
                    user = document.createElement('option')
                    user.innerText = users_list[i][1];
                    user.value = users_list[i][0];
                    user.selected = users_list[i][1] == username ? true : false;
                    users_select.appendChild(user);
                }
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function change_mission() {
    user = document.getElementById('select-user').value;
    name = document.getElementById('name-mission').value;
    reward = document.getElementById('reward').value;
    reports = document.getElementById('count-reports').value;
    date = document.getElementById('time').value.replace('T',' ');

    if (user === '' || name === '' || reward === '' || reports === '' || date === '')
        window.Telegram.WebApp.showAlert('Заполните все поля!');

    json = {
        user: user,
        name: name,
        reward: reward,
        reports: reports,
        date: date
    }

    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href + '/change', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(json)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.location.reload()
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function init_map() {
    var element = document.getElementById('popup');
    const content = document.getElementById('popup-content');
    const closer = document.getElementById('popup-closer');



    var overlay  = new ol.Overlay({
        element: element,
        positioning: 'bottom-center',
        stopEvent: false
    });


    closer.onclick = function () {
        overlay.setPosition(undefined);
        closer.blur();
        return false;
    };


    map = new ol.Map({
        target: "map",
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM({
                      url: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
                })
            }),
            new ol.layer.Vector({
                source: new ol.source.Vector({
                    url: window.location.href+'/geojson',
                    format: new ol.format.GeoJSON()
                }),
                style: new ol.style.Style({
                    image: new ol.style.Icon(({
                        anchor: [0.5, 64],
                        anchorXUnits: 'fraction',
                        anchorYUnits: 'pixels',
                        scale: 0.5,
                        src: 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png'
                    }))
                })
            })
        ],
        overlays: [overlay],
        view: new ol.View({
                center: ol.proj.fromLonLat([30.40346935341173, 60.06635279189136]),
                zoom: 15
        })
    });


    // Add an event handler for the map "singleclick" event
    map.on('singleclick', function(evt) {

        // Attempt to find a feature in one of the visible vector layers
        var feature = map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
            return feature;
        });

        if (feature) {

            var coord = feature.getGeometry().getCoordinates();
            var props = feature.getProperties();
            var info = `${feature.get('iconCaption')} ${feature.get('uuid')}`;

            content.innerHTML = info;
            // Offset the popup so it points at the middle of the marker not the tip
            overlay.setPosition(evt.coordinate);

        }

    });
}