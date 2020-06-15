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

function toggleUnselectedVoteButtonsInSameCandidatePosition(candidatesDiv) {
    var numCandidateButtons = candidatesDiv.getElementsByTagName('button');
    for (var i = 0; i < numCandidateButtons.length; i++) {
        if (numCandidateButtons[i].classList.contains('vote-btn')) {
            numCandidateButtons[i].disabled = true;
            numCandidateButtons[i].classList.add('disabled-vote-btn');
            numCandidateButtons[i].classList.remove('vote-btn');
        } else if (numCandidateButtons[i].classList.contains('disabled-vote-btn')) {
            numCandidateButtons[i].disabled = false;
            numCandidateButtons[i].classList.add('vote-btn');
            numCandidateButtons[i].classList.remove('disabled-vote-btn');
        }
    }
}

function getNumSelectedCandidatesInSamePosition(candidatesDiv) {
    var numSelectedButtons = candidatesDiv.getElementsByTagName('button');
    var numSelected = 0;
    for (var i = 0; i < numSelectedButtons.length; i++) {
        if (numSelectedButtons[i].classList.contains('depressed-vote-btn')) {
            numSelected++;
        }
    }

    return numSelected;
}

function getMaxNumSelectedCandidatesInSamePosition(candidatesDiv) {
    var maxNumSelected = candidatesDiv.getAttribute('data-max-num-selected');
    return maxNumSelected;
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
                var candidatesDiv = this.parentNode.parentNode;
                var numSelected = getNumSelectedCandidatesInSamePosition(candidatesDiv);
                var maxNumSelected = getMaxNumSelectedCandidatesInSamePosition(candidatesDiv);
                if (this.classList.contains('depressed-vote-btn')) {
                    // This button was clicked already.
                    if (maxNumSelected > 1) {
                        // This block should only be allowed for candidate positions that allow
                        // for more than one candidate to be selected, to ensure auto-switching
                        // candidates for a position when the voter can only select one.
                        numSelected--;
                        if ((numSelected + 1) == maxNumSelected) {
                            // Previously, the currently unselected voting buttons were disabled. Enable them now
                            // since we have an additional slot.
                            toggleUnselectedVoteButtonsInSameCandidatePosition(candidatesDiv);
                        }
                    }

                    // And now, revert this button to an unselected state. We have to this last. Otherwise
                    // this button will be considered previously disabled.
                    resetVotingButton(this);
                } else {
                    // This button was not clicked before.
                    if (maxNumSelected == 1) {
                        // Allow auto-switching candidates when you can only vote for one for a position.
                        resetAllVotingButtonsInSameCandidatePosition(this);

                        this.textContent = 'Unvote';
                        this.classList.add('depressed-vote-btn');
                        this.classList.remove('vote-btn')

                        var candidateDiv = this.parentNode;
                        candidateDiv.classList.add('opaque');
                    } else {
                        // Note that when the position allows for choosing more than one candidate, Botos
                        // will require voters to manually unvote candidates. This is so that they can make
                        // sure that they do not accidentally and unintentionally unvote a candidate they
                        // were actually voting for. If Botos auto-unvotes a candidate when a voter attempts
                        // to vote for one more candidate, it would put an additional mental load on the
                        // voter since they would have to track which candidate will be unvoted, depending on
                        // the mechanism for auto-unvoting.
                        if (numSelected < maxNumSelected) {
                            this.textContent = 'Unvote';
                            this.classList.add('depressed-vote-btn');
                            this.classList.remove('vote-btn')

                            var candidateDiv = this.parentNode;
                            candidateDiv.classList.add('opaque');

                            numSelected++; // Since we selected a new one.
                            if (numSelected == maxNumSelected) {
                                // Time to disable other buttons.
                                toggleUnselectedVoteButtonsInSameCandidatePosition(candidatesDiv);
                            }
                        }
                    }
                }
            });
        });
    }

    var castVoteForm = document.querySelector('form#voting');
    if (castVoteForm != null) {
        castVoteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var castVote = confirm('Are you sure you want to cast your vote?');

            if (castVote) {
                castVoteForm.querySelector('input[type=submit').disabled = true;

                var votedCandidates = [];
                var votingButtons = document.querySelectorAll('button.depressed-vote-btn');
                votingButtons.forEach(btn => {
                    votedCandidates.push(btn.value);
                });
            
                var candidatesVotedInput = castVoteForm.querySelector('input#candidates-voted');
                candidatesVotedInput.value = JSON.stringify(votedCandidates);
                this.submit();
            } else {
                return false;
            }
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

    // Voted sub-view.
    var logoutBtn = document.querySelector('button.logout-btn');
    if (logoutBtn != null) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();

            this.disabled = true;

            var logoutForm = document.querySelector('form#logout');
            logoutForm.submit();
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
