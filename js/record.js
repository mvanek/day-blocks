(function() {
    'use strict';
    function day_click_callback(e) {
        toggle_node(e.target);
    }

    function send_request(method, date) {
        var data, xhr;
        data = new FormData();
        data.append('method', method);
        data.append('date', date);
        xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log(xhr.status);
                console.log(xhr.responseText);
            }
        };
        xhr.open('post', window.location.href);
        xhr.send(data);
    }

    function set_date(date) {
        send_request('set', date);
    }

    function set_name(name) {
        send_request('set_name', name);
    }

    function set_start(date) {
        send_request('set_start', date);
    }

    function toggle_node(dayNode) {
        var date;
        date = dayNode.querySelector('.tooltip').textContent;
        if (dayNode.classList.contains('set')) {
            unset_date(date);
            dayNode.classList.remove('set');
        } else {
            set_date(date);
            dayNode.classList.add('set');
        }
    }

    function unset_date(date) {
        send_request('unset', date);
    }

    var dayNodes, i;
    dayNodes = document.getElementsByClassName('day');
    for (i=0; i<dayNodes.length; i++) {
        dayNodes[i].addEventListener('click', day_click_callback, false);
    }
}());
