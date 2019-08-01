function ready(fn) {
    if (document.readyState != 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

function resetVotingButton(btn) {
    btn.textContent = 'Vote';
    btn.classList.add('vote-btn');
    btn.classList.remove('depressed-vote-btn');

    var candidateDiv = btn.parentNode;
    candidateDiv.classList.remove('opaque');
}

function resetAllVotingButtonsInSameCandidatePosition(btn) {
    var positionCandidates = btn.parentNode.parentNode;
    var votingButtons = positionCandidates.getElementsByTagName('button');
    for (var i = 0; i < votingButtons.length; i++) {
        var btn = votingButtons[i];
        resetVotingButton(btn);
    }
}

ready(function() {
    // Login sub-view.
    var loginForm = document.querySelector('form#login');
    if (loginForm != null) {
        loginForm.addEventListener('submit', function() {
            this.querySelector('input[type=submit]').disabled = true;
        });
    }

    // Voting sub-view.
    var votingButtons = document.querySelectorAll('.vote-btn');
    if (votingButtons != null) {
        votingButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                if (this.classList.contains('depressed-vote-btn')) {
                    // This button was clicked already.
                    resetVotingButton(this);
                } else {
                    // This button was not clicked before.
                    resetAllVotingButtonsInSameCandidatePosition(this);

                    this.textContent = 'Unvote';
                    this.classList.add('depressed-vote-btn');
                    this.classList.remove('vote-btn')

                    var candidateDiv = this.parentNode;
                    candidateDiv.classList.add('opaque');
                }
            });
        });
    }

    var meme1Trigger = document.getElementById('meme-1');
    if (meme1Trigger != null) {
        var votingHeader = document.querySelector('header#voting');
        meme1Trigger.addEventListener('click', function() {
            var memeIntro = votingHeader.querySelector('h1');
            var memeBody = votingHeader.querySelector('p');

            memeIntro.textContent = 'WHAAAT?';
            memeBody.textContent = 'You never played Tuber Simulator???';

            window.scrollTo(0, 0);
        });
    }

    var logoutLink = document.getElementById('logout-link');
    if (logoutLink != null) {
        logoutLink.addEventListener('click', function() {
            var request = new XMLHttpRequest();
            request.onreadystatechange = function() {
                document.location.reload(true);
            };
            request.open('POST', '/auth/logout', true);
            request.setRequestHeader('X-CSRFToken', window.CSRF_TOKEN);
            request.send({});
        });
    }

    var castVoteForm = document.querySelector('form#voting');
    if (castVoteForm != null) {
        castVoteForm.addEventListener('submit', function() {
            var votedCandidates = [];
            var votingButtons = document.querySelectorAll('button.depressed-vote-btn');
            votingButtons.forEach(btn => {
                votedCandidates.push(btn.value);
            });
            
            var candidatesVotedInput = castVoteForm.querySelector('input#candidates-voted');
            candidatesVotedInput.value = JSON.stringify(votedCandidates);
        });
    }
})
