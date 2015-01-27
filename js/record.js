(function() {
    'use strict';
    function day_click_callback(e) {
        toggle_node(e.target);
    }

    function send_request(method, id, date) {
        var data = new FormData(),
            xhr = new XMLHttpRequest();
        data.append('method', method);
        data.append('date', date);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log(xhr.status);
                console.log(xhr.responseText);
            }
        };
        xhr.open('post', '/r/'+id);
        xhr.send(data);
    }

    function set_date(id, date) {
        send_request('set', id, date);
    }

    function set_name(id, name) {
        send_request('set_name', id, name);
    }

    function set_start(id, date) {
        send_request('set_start', id, date);
    }

    function toggle_node(dayNode) {
        var date = dayNode.querySelector('.tooltip').textContent,
            id = dayNode.parentNode.parentNode.id.split('-')[1];
        if (dayNode.classList.contains('set')) {
            unset_date(id, date);
            dayNode.classList.remove('set');
        } else {
            set_date(id, date);
            dayNode.classList.add('set');
        }
    }

    function unset_date(id, date) {
        send_request('unset', id, date);
    }

    var dayNodes = document.getElementsByClassName('day'),
        viewForms = document.querySelectorAll('.record form'),
        i, j;
    /* Sync all day nodes with server */
    for (i=0; i<dayNodes.length; i++) {
        dayNodes[i].addEventListener('click', day_click_callback, false);
    }
    /* User layout controls */
    for (i=0; i<viewForms.length; i++) {
        viewForms[i].addEventListener('change', function(e) {
            var curButton,
                viewForm = e.target.parentNode,
                layoutButtons = viewForm.layout;
            for (j=0; j<layoutButtons.length; j++) {
                curButton = layoutButtons[j];
                if (curButton.checked) {
                    viewForm.parentNode.classList.add(curButton.value);
                } else {
                    viewForm.parentNode.classList.remove(curButton.value);
                }
            }
        }, false);
    }
}());
