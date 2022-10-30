function hide_popup(elem) {
    popup = document.getElementById(elem);
    popup.style.display = 'None';
    let video = popup.querySelectorAll('iframe');
    for (var i = 0; i < video.length; i++){
        video[i].src = '';
    }
}

function show_popup(elem) {
    popup = document.getElementById(elem);
    popup.style.display = 'block';
}