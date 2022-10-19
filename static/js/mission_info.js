var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', '/validate', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if (xmlhttp.status == 401) window.location.href = '/unauthorized';
    }
};

// var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
// xmlhttp.open('GET', window.location.href + '/report', true); // Открываем асинхронное соединение
// xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
// xmlhttp.send(); // Отправляем POST-запрос
// xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
//     if (xmlhttp.readyState == 4) { // Ответ пришёл
//         if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
//             json = JSON.parse(this.responseText);
//             reports = document.getElementById("reports");
//
//             for (var i = 0; i < json.length; i++) {
//                 item = document.createElement('button');
//                 item.type = 'button';
//                 item.className = 'collapsible';
//                 item.innerText = 'Отчет ' + (i+1);
//                 reports.appendChild(item);
//
//                 report = document.createElement('div');
//                 report.className = 'report-grid';
//
//                 images = document.createElement('div');
//                 images.className = 'report-grid-photos'
//                 for (var j = 0; j < json[i]['photos'].length; j++) {
//                     photo = document.createElement('img');
//                     photo.className = 'report-grid-photo';
//                     photo.src = `/get_file?file_id=${json[i]['photos'][j]}`;
//                     photo.loading = 'lazy';
//                     images.appendChild(photo);
//                 }
//                 report.appendChild(images)
//
//                 video = document.createElement('iframe');
//                 video.src = `/get_file?file_id=${json[i]['video']}`;
//                 report.appendChild(video);
//
//                 reports.appendChild(report)
//             }
//             add_coll_listener()
//         }
//         else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
//     }
// };
function report_block() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/report', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                var json = JSON.parse(this.responseText);

                var reports_buttons = document.getElementById('reports');

                for (var i = 0; i < json.length; i++) {
                    var btn_report = document.createElement('button');
                    btn_report.className = 'button';
                    btn_report.innerText = `Отчет №${json[i]['id']}\nДом ${json[i]['building_id']+1}`;

                    const data = json[i];
                    const idx = i;
                    const count_reports = json.length;
                    btn_report.id = `report_${idx+1}`;
                    btn_report.addEventListener('click', function () {
                            document.getElementById('next-report-button').name = `report_${count_reports == idx+1 ? 1 : idx+2 }`;
                            document.getElementById('prev-report-button').name = `report_${idx == 0 ? (count_reports) : idx }`;

                            document.getElementById('delete_report').name = `${data['date']}`;

                            document.getElementById('report-name').innerText =
                                `Отчет №${data['id']} Дом ${data['building_id']+1}`;

                            media = document.getElementById('media');
                            media.innerHTML = '';
                            media.innerText = '';

                            images = document.createElement('div');
                            images.className = 'report-grid-photos'
                            for (var j = 0; j < data['photos'].length; j++) {
                                photo = document.createElement('img');
                                photo.className = 'report-grid-photo';
                                photo.src = `/get_file?file_id=${data['photos'][j]}`;
                                photo.loading = 'lazy';
                                images.appendChild(photo);
                            }
                            media.appendChild(images)

                            video = document.createElement('iframe');
                            video.src = `/get_file?file_id=${data['video']}&`;
                            video.setAttribute('autoplay', '0');
                            video.setAttribute('mute', '1');
                            media.appendChild(video);

                            popup = document.getElementById('report-popup');
                            popup.style.display = 'block';
                        }, false
                    )

                    reports_buttons.appendChild(btn_report);
                }
            }
        }
    };
}

function delete_report(id) {
    var user_id = document.getElementById('user-id').name;
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href+'/delete_report', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify([id, user_id])); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                document.location.reload(true)
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}


function show_popup_report(id) {
    popup = document.getElementById('report-popup');
    popup.style.display = 'block';

    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/report', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                json = JSON.parse(this.responseText);
                media = document.getElementById('media');
                media.innerHTML = '';
                media.innerText = '';

                for (var i = 0; i < json.length; i++) {
                    if (json[i]['id'] != id) continue;

                    document.getElementById('next-report-button').name = `report_${(json.length) == id ? 1 : id+1 }`;
                    document.getElementById('prev-report-button').name = `report_${id == 1 ? (json.length) : id-1 }`;

                    document.getElementById('report-name').innerText =
                                `Отчет №${json[i]['id']} Дом ${json[i]['building_id']+1}`;

                    document.getElementById('delete_report').name = `${json[i]['date']}`;
                    images = document.createElement('div');
                    images.className = 'report-grid-photos'
                    for (var j = 0; j < json[i]['photos'].length; j++) {
                        photo = document.createElement('img');
                        photo.className = 'report-grid-photo';
                        photo.src = `/get_file?file_id=${json[i]['photos'][j]}`;
                        photo.loading = 'lazy';
                        images.appendChild(photo);
                    }
                    media.appendChild(images)

                    video = document.createElement('iframe');
                    video.src = `/get_file?file_id=${json[i]['video']}&`;
                    video.setAttribute('autoplay', '0');
                    video.setAttribute('mute', '1');
                    media.appendChild(video);
                }
                add_coll_listener()
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

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
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href + '/center_map', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                const element = document.getElementById('popup');
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

                var style = new ol.style.Style({
                    image: new ol.style.Icon(({
                        anchor: [0.5, 64],
                        anchorXUnits: 'fraction',
                        anchorYUnits: 'pixels',
                        scale: 0.5,
                        src: 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png',
                    })),
                    stroke: new ol.style.Stroke({
                        color: "red",
                        width: 2
                    }),
                    text: new ol.style.Text({
                        placement: 'Point',
                        text: '1',
                        font: 'bold 16px Times New Roman',
                        offsetY: -20,
                        fill: new ol.style.Fill({color: 'rgb(0,0,0)'}),
                        stroke: new ol.style.Stroke({color: 'rgb(255,255,255)', width: 1})
                    })
                });

                var styleFunction = function(feature) {
                    var text = `${feature.getProperties()['iconContent']}`;
                    if (text == 'undefined')
                        text = ''
                    style.getText().setText(text);
                    return style;
                }

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
                            style: styleFunction
                        })
                    ],
                    overlays: [overlay],
                    view: new ol.View({
                            center: ol.proj.fromLonLat(JSON.parse(this.responseText)),
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
                        var d = new Date();
                        var gmtHours = -d.getTimezoneOffset()/60;


                        var coord = feature.getGeometry().getCoordinates();
                        var props = feature.getProperties();
                        var info = `${props['iconCaption']}<br>`;
                        info += new Date((props['unix'] + gmtHours*60*60)*1000).toISOString().slice(0,19).replace('T',' ');
                        info += `<br>Номер дома: ${props['building']+1}`;
                        var btn = document.getElementById('btn-report');
                        btn.onclick = function () {
                            show_popup_report(props['id']);
                        };

                        content.innerHTML = info;
                        // Offset the popup so it points at the middle of the marker not the tip
                        overlay.setPosition(evt.coordinate);

                    }

                });
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function download_report(url) {
    window.Telegram.WebApp.showAlert('Отчет формируется.\nОжидайте когда он вам придет в сообщения');
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', url, true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.Telegram.WebApp.showAlert('Отчет отправлен!');
            }
            else if (xmlhttp.status == 401) window.location.href = '/unauthorized';
        }
    };
}

function change_report(name) {
    var open_report = new Event('click');
    var slide = new Event('slide');

    var block = document.getElementById('animation-popup');
    block.dispatchEvent(slide);
    // block.classList.add('change-slide');
    document.getElementById(name).dispatchEvent(open_report);

    // block.addEventListener('animationend', function () {
    //     this.classList.remove('change-slide');
    // })
}

// if (!/constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && window['safari'].pushNotification)))
//     document.getElementById('animation-popup').addEventListener('slide', function () {
//         this.classList.remove('change-slide');
//     })