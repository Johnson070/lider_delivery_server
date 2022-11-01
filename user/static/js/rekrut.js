var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
xmlhttp.open('GET', '/delivery_bot/user/validate', true); // Открываем асинхронное соединение
xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
xmlhttp.send(); // Отправляем POST-запрос
xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
    if (xmlhttp.readyState == 4) { // Ответ пришёл
        if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
    }
};

async function save_rekrut() {
    let full_name = document.getElementById('full_name').value;
    let birthday = document.getElementById('birthday').value;
    let region = document.getElementById('region').value;
    let qualities = document.getElementById('qualities').value;
    let info = document.getElementById('info').value;
    let reward = document.getElementById('reward').value;
    let time_work = document.getElementById('time_work').value;
    let national = document.getElementById('national').value;
    let photo = document.getElementById('photo').files[0];

    if (full_name.match(/(.+)/) == null || birthday === undefined || region === '' || qualities === '' ||
        info === '' || photo === undefined) {
        window.parent.window.Telegram.WebApp.showAlert('Все поля обязательны к заполнению!');
        return;
    }

    photo = await photo.arrayBuffer()

    photo = Array.from(new Uint8Array(photo))

    json = {
        full_name: full_name,
        birthday: birthday,
        region: region,
        qualities: qualities,
        info: info,
        reward: reward,
        photo: photo,
        time_work: time_work,
        national: national
    }

    window.parent.window.Telegram.WebApp.showAlert('Ожидайте!');
    document.getElementById('rekrut-form').style.display = 'none';
    var xmlhttp = new XMLHttpRequest(); // Создаём объект XMLHTTP
    xmlhttp.open('POST', '/delivery_bot/user/rekrut', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/json'); // Отправляем кодировку
    xmlhttp.send(JSON.stringify(json)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
        if (xmlhttp.readyState == 4) { // Ответ пришёл
            if (xmlhttp.status == 200) {
              window.parent.window.Telegram.WebApp.showAlert('Ожидайте, когда ваша анкета будет одобрена');
              window.location.reload();
            }
            else if (xmlhttp.status == 401) location.replace('/delivery_bot/unauthorized');
            else {
                window.parent.window.Telegram.WebApp.showAlert('Произошла ошибка.\nПопробуйте позже.');
            }
        }
    };
}