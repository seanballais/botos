function ready(fn) {
    if (document.readyState != 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

ready(function() {
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
        forms[i].addEventListener('submit', function() {
            this.querySelector('input[type=submit]').disabled = true;
        });
    }
})
