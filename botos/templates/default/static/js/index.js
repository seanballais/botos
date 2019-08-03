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

    var castVoteForm = document.querySelector('form#voting');
    if (castVoteForm != null) {
        castVoteForm.addEventListener('submit', function() {
            castVoteForm.querySelector('input[type=submit').disabled = true;

            var votedCandidates = [];
            var votingButtons = document.querySelectorAll('button.depressed-vote-btn');
            votingButtons.forEach(btn => {
                votedCandidates.push(btn.value);
            });
            
            var candidatesVotedInput = castVoteForm.querySelector('input#candidates-voted');
            candidatesVotedInput.value = JSON.stringify(votedCandidates);
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

    // Voted sub-view.
    var logoutBtn = document.querySelector('button.logout-btn');
    if (logoutBtn != null) {
        logoutBtn.addEventListener('click', function() {
            logoutBtn.disabled = true;
            
            // Had to duplicate this from `logoutLink`. I tried put the snippet
            // below in a function but it doesn't seem to work.
            var request = new XMLHttpRequest();
            request.onreadystatechange = function() {
                document.location.reload(true);
            };
            request.open('POST', '/auth/logout', true);
            request.setRequestHeader('X-CSRFToken', window.CSRF_TOKEN);
            request.send({});
        });
    }

    var meme2Trigger = document.querySelector('a#meme-2');
    if (meme2Trigger != null) {
        meme2Trigger.addEventListener('click', function() {
            var votedHeaderBlock = document.querySelector('header#voted');
            var votedArticleBlock = document.querySelector('article#voted');
            var memeBlock = document.querySelector('article#meme-block');

            votedHeaderBlock.classList.add('hide');
            votedArticleBlock.classList.add('hide');
            memeBlock.style.display = 'flex';

            var rickRollVideo = memeBlock.querySelector('video');
            rickRollVideo.loop = true;
            rickRollVideo.play();
        });
    }

    var meme2Exit = document.querySelector('button#meme-2-exit');
    if (meme2Exit != null) {
        meme2Exit.addEventListener('click', function() {
            let randomMessages = [
                'Who is responsible for this?',
                'WTF? LET ME OUT NOW.',
                'AAAAHHHHHH! THE HORROR!',
                'Why? Oh, why?',
                'OH HAIL, WATERSHEEP! (DING DING DING) Please let me out!',
                'HUHUHUHUHUHUHU. What did I ever do to you?',
                'Dude! Rick-rolling is soooooooooo late 2000s/early 2010s.',
                'You do note the liar is ma peyk. Huhu.',
                'Sorry for wanting to ruin the elections. :(',
                'Noooooooooooooooooooo!!!'
            ];

            let randomMessage = randomMessages[Math.floor(Math.random() * randomMessages.length)];
            meme2Exit.textContent = randomMessage;

            let randomNum = Math.floor(Math.random() * 100);
            if (randomNum < 25) {
                meme2Exit.textContent = 'You are now free.';
                meme2Exit.disabled = true;

                document.location.reload(true);
            }            
        });
    }
})
