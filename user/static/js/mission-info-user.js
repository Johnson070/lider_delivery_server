function change_report(name) {
    var open_report = new Event('click');
    document.getElementById(name).dispatchEvent(open_report);
}

function get_costs_types() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href+'/get_reports_types', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                let sel = document.getElementById('type-report');

                let json = JSON.parse(this.responseText);

                for (var i = 0; i < Object.keys(json).length; i++){
                    var opt = document.createElement('option');
                    opt.innerText = json[i][0];
                    opt.value = i;
                    sel.appendChild(opt);
                }
            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
        }
    };
}


function get_tag_day() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href+'/hash', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                document.getElementById('tag_day').innerText = this.responseText;

            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
        }
    };
}

function errorHandler(err) {
        if(err.code == 1) {
           window.parent.window.Telegram.WebApp.showAlert("Error: Access is denied!");
        }
        else if( err.code == 2) {
           window.parent.window.Telegram.WebApp.showAlert("Error: Position is unavailable!");
        }
        else {
           window.parent.window.Telegram.WebApp.showAlert(`Произошла ошибка перезагрузите страницу!\n`+
               `${err.message}`);
        }
    }

function get_location_save_report(){
    geolocation.setTracking(false);
    if(navigator.geolocation && geolocation.getPosition() !== undefined){
        save_report(ol.proj.toLonLat(geolocation.getPosition()))
    } else{
        window.parent.window.Telegram.WebApp.showAlert("Ваш браузер не поддерживает отслеживание геолокации," +
            " смените WebView настройках или поменяйте телефон.");
    }
}

function end_mission() {
    window.parent.window.Telegram.WebApp.showConfirm('Вы уверены что хотите завершить задание?\n' +
        'Вы не сможете после этого вы не сможете удалять или добавлять отчеты.', function (state) {
        if (state) confirm_pass_mission();
    })
}

function confirm_pass_mission() {
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('GET', window.location.href+'/pass', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                window.location.reload()
            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
        }
    };
}

async function save_report(location) {
    let selection = document.getElementById('type-report');
    let type_report = selection[selection.selectedIndex].value;
    let photos = document.getElementById('photo-report').files;
    let video = document.getElementById('video-report').files;

    let size = 0;
    for (var i = 0; i < photos.length; i++)
        size += photos[i].size;

    if (photos.length == 0 || video.length == 0) {
        window.parent.window.Telegram.WebApp.showAlert('Все поля обязательны к заполнению');
        return;
    }
    else if (size / 1024.0 / 1024.0 > 10) {
        window.parent.window.Telegram.WebApp.showAlert('Размер ФОТО должен быть меньше 10 Мб!\n' +
            'При выборе медиа файлов выберите максимальное сжатие!');
        return;
    }

    json = {
        photos: [],
        video: null,
        type_report: type_report,
        lat: location[1],
        lon: location[0]
    }

    for (var i = 0; i < photos.length; i++) {
        json['photos'].push(Array.from(new Uint8Array(await photos[i].arrayBuffer())));
    }
    json['video'] = Array.from(new Uint8Array(await video[0].arrayBuffer()));

    hide_popup('add-report-popup');
    window.parent.window.Telegram.WebApp.showAlert('Ожидайте.');
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open('POST', window.location.href + '/add_report', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(json)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 401) location.replace('/manage_bot/unauthorized');
            else if (xmlhttp.status == 200) {
                if (this.responseText == '0') window.location.reload();
                else if (this.responseText === '1') {
                    window.parent.window.Telegram.WebApp.showAlert('Кажется вы ушли слишком делако от дома.\n' +
                        'Не уходите с места где вы размещали рекламу.\n' +
                        'Если вы уйдете далеко от точки, то отчет не будет принят.');
                }
                else if (this.responseText === '2') {
                    window.parent.window.Telegram.WebApp.showAlert('Кажется вы перемещяетесь слишком быстро.\n' +
                        'За повторное нарушение вам будет начислен штраф!');
                }
                else if (this.responseText === '3') {
                    window.parent.window.Telegram.WebApp.showAlert('Вы отправили фото или видео которое уже отправляли.\n' +
                        'Удалите дубликаты и отправьте заново.');
                }
                else if (this.responseText === '-1') {
                    window.parent.window.Telegram.WebApp.showAlert('Отправка отчетов заблокирована!\n' +
                        'Перезагрузите страницу!');
                }
            }
            else {
                window.parent.window.Telegram.WebApp.showAlert('Произошла ошибка попробуйте снова.')
            }
        }
    };
    geolocation.setTracking(true);
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

                var style_geojson = new ol.style.Style({
                    image: new ol.style.Icon(({
                        anchor: [0.5, 64],
                        anchorXUnits: 'fraction',
                        anchorYUnits: 'pixels',
                        scale: 0.5,
                        src: 'https://maps.google.com/mapfiles/kml/paddle/ylw-blank.png',
                    })),
                    stroke: new ol.style.Stroke({
                        color: "red",
                        width: 2
                    }),
                    text: new ol.style.Text({
                        placement: '',
                        text: '1',
                        font: 'bold 16px Times New Roman',
                        offsetY: -20,
                        fill: new ol.style.Fill({color: 'rgb(0,0,0)'}),
                        stroke: new ol.style.Stroke({color: 'rgb(255,255,255)', width: 1})
                    })
                });

                var style_buildings = new ol.style.Style({
                    image: new ol.style.Icon(({
                        anchor: [0.5, 64],
                        anchorXUnits: 'fraction',
                        anchorYUnits: 'pixels',
                        scale: 0.5,
                        src: 'https://maps.google.com/mapfiles/kml/paddle/red-blank.png',
                    })),
                    stroke: new ol.style.Stroke({
                        color: "red",
                        width: 2
                    })
                });

                var styleFunction = function(feature) {
                    var text = `${feature.getProperties()['iconContent']}`;
                    if (text == 'undefined')
                        text = ''
                    style_geojson.getText().setText(text);
                    return style_geojson;
                }

                const view = new ol.View({
                            center: ol.proj.fromLonLat(JSON.parse(this.responseText)),
                            zoom: 15
                    })

                map = new ol.Map({
                    target: "map",
                    layers: [
                        new ol.layer.Tile({
                            source: new ol.source.OSM({
                                url: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            })
                        })
                    ],
                    overlays: [overlay],
                    view: view
                });

                geolocation = new ol.Geolocation({
                    trackingOptions: {
                        enableHighAccuracy: true,
                    },
                    projection: view.getProjection(),
                });

                function showLocation(position) {}
                function errorHandler(err) {
                    if(err.code == 1) {
                       window.parent.window.Telegram.WebApp.showAlert("Error: доступ к геолокации запрещен!");
                    }
                    else if( err.code == 2) {
                       window.parent.window.Telegram.WebApp.showAlert("Error: геопозиционирование не доступно!");
                    }
                    show_popup('location-popup');
                }
                function getLocation(){
                    if(navigator.geolocation){
                       // timeout at 60000 milliseconds (60 seconds)
                       var options = {maximumAge: 10000, timeout:10000, enableHighAccuracy: true};
                       navigator.geolocation.getCurrentPosition(showLocation, errorHandler, options);
                    } else{
                       window.parent.window.Telegram.WebApp.showAlert("Ваш браузер не поддерживает отслеживание геолокации," +
            " смените WebView настройках или поменяйте телефон.");
                    }
                }

                geolocation.setTracking(true);

                const accuracyFeature = new ol.Feature();
                geolocation.on('change:accuracyGeometry', function () {
                  accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
                });

                const positionFeature = new ol.Feature();
                positionFeature.setStyle(
                  new ol.style.Style({
                    image: new ol.style.Circle({
                      radius: 6,
                      fill: new ol.style.Fill({
                        color: '#3399CC',
                      }),
                      stroke: new ol.style.Stroke({
                        color: '#fff',
                        width: 2,
                      }),
                    }),
                  })
                );

                geolocation.on('change:position', function () {
                  const coordinates = geolocation.getPosition();
                  map.getView().setCenter(coordinates);
                  positionFeature.setGeometry(coordinates ? new ol.geom.Point(coordinates) : null);
                });

                new ol.layer.Vector({
                  map: map,
                  source: new ol.source.Vector({
                    features: [accuracyFeature, positionFeature],
                  })
                });

                new ol.layer.Vector({
                    map: map,
                    source: new ol.source.Vector({
                        url: window.location.href+'/geojson',
                        format: new ol.format.GeoJSON()
                    }),
                    style: styleFunction
                });

                new ol.layer.Vector({
                    map: map,
                    source: new ol.source.Vector({
                        url: window.location.href+'/geojson_buildings',
                        format: new ol.format.GeoJSON()
                    }),
                    style: style_buildings
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

                        if (props['uuid'] == undefined || ['uuid'] == 'building') return;

                        var info = `${props['iconCaption']}<br>`;
                        info += new Date((props['unix'] + gmtHours*60*60)*1000).toISOString().slice(0,19).replace('T',' ');

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
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
        }
    };
}


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
                    btn_report.innerText = `Отчет №${json[i]['id']}
                    ${json[i]['building_id']}`;

                    const data = json[i];
                    const idx = i;
                    const count_reports = json.length;
                    btn_report.id = `report_${idx+1}`;
                    btn_report.addEventListener('click', function () {
                            document.getElementById('next-report-button').name = `report_${count_reports == idx+1 ? 1 : idx+2 }`;
                            document.getElementById('prev-report-button').name = `report_${idx == 0 ? (count_reports) : idx }`;

                            document.getElementById('delete_report').name = `${data['date']}`;
                            document.getElementById('tag_report').innerText = `${data['tag']}`;
                            
                            document.getElementById('report-name').innerText =
                                `Отчет №${data['id']}
                                ${data['building_id']}`;

                            media = document.getElementById('media');
                            media.innerHTML = '';
                            media.innerText = '';

                            images = document.createElement('div');
                            images.className = 'report-grid-photos'
                            for (var j = 0; j < data['photos'].length; j++) {
                                photo = document.createElement('img');
                                photo.className = 'report-grid-photo';
                                photo.src = `/delivery_bot/user/get_file?file_id=${data['photos'][j]}`;
                                photo.loading = 'lazy';
                                images.appendChild(photo);
                            }
                            media.appendChild(images)

                            video = document.createElement('iframe');
                            video.src = `/delivery_bot/user/get_file?file_id=${data['video']}`;
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
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', window.location.href+'/delete_report', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify([id])); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
                document.location.reload(true)
            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
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
                                `Отчет №${json[i]['id']}
                                ${json[i]['building_id']}`;

                    document.getElementById('delete_report').name = `${json[i]['date']}`;
                    document.getElementById('tag_report').innerText = `${json[i]['tag']}`;
                    images = document.createElement('div');
                    images.className = 'report-grid-photos'
                    for (var j = 0; j < json[i]['photos'].length; j++) {
                        photo = document.createElement('img');
                        photo.className = 'report-grid-photo';
                        photo.src = `/delivery_bot/user/get_file?file_id=${json[i]['photos'][j]}`;
                        photo.loading = 'lazy';
                        images.appendChild(photo);
                    }
                    media.appendChild(images)

                    video = document.createElement('iframe');
                    video.src = `/delivery_bot/user/get_file?file_id=${json[i]['video']}`;
                    video.setAttribute('autoplay', '0');
                    video.setAttribute('mute', '1');
                    media.appendChild(video);
                }
                add_coll_listener()
            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
        }
    };
}