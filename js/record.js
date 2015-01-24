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

    var dayNodes = document.getElementsByClassName('day'),
        viewForm = document.forms.view,
        i;
    /* Sync all day nodes with server */
    for (i=0; i<dayNodes.length; i++) {
        dayNodes[i].addEventListener('click', day_click_callback, false);
    }
    /* User layout controls */
    viewForm.addEventListener('change', function(e) {
        var curButton,
            layoutButtons = viewForm.layout;
        for (i=0; i<layoutButtons.length; i++) {
            curButton = layoutButtons[i];
            if (curButton.checked) {
                viewForm.parentNode.classList.add(curButton.value);
            } else {
                viewForm.parentNode.classList.remove(curButton.value);
            }
        }
    }, false);
}());
