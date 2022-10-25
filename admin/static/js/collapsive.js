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
