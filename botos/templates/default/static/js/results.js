ready(function() {
    var tabLinks = document.querySelectorAll('.tab-link');
    if (tabLinks != null) {
        tabLinks.forEach(link => {
            link.addEventListener('click', function() {
                var activeTabLink = document.querySelector(
                    '.active-election-link'
                );
                activeTabLink.classList.remove('active-election-link');

                var linkItem = this.parentNode;
                linkItem.classList.add('active-election-link');
            });
        });
    }

    var adminBackLink = document.getElementById('admin-backlink');
    if (adminBackLink != null) {
        adminBackLink.addEventListener('click', function() {
            this.classList.add('clicked-link');
        });
    }
});
