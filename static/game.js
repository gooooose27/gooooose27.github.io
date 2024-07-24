document.addEventListener('DOMContentLoaded', () => {
    let score = 0;
    let totalGuesses = 0;
    let realRight = 0;
    let realWrong = 0;
    let fakeRight = 0;
    let fakeWrong = 0;
    let guesses = 0;

    const imageElement = document.getElementById('image');
    const scoreElement = document.getElementById('score');
    const feedbackElement = document.getElementById('feedback');
    const aiButton = document.getElementById('ai-button');
    const realButton = document.getElementById('real-button');

    const loadNewImage = () => {
        fetch('/get_image')
            .then(response => {
                if (!response.ok) {
                    throw new Error('No new images available');
                }
                return response.json();
            })
            .then(data => {
                imageElement.src = `data:image/jpeg;base64,${data.image}`;
                imageElement.dataset.isAi = data.is_ai;
            })
            .catch(error => {
                feedbackElement.innerText = error.message;
                aiButton.disabled = true;
                realButton.disabled = true;
            });
    };

    const checkGuess = (isAiGuess) => {
        const isAi = imageElement.dataset.isAi === 'true';
        totalGuesses++;
        guesses++;

        if (isAiGuess === isAi) {
            score++;
            feedbackElement.innerText = "Correct!";
        } else {
            feedbackElement.innerText = "Incorrect.";
        }

        if (isAiGuess && isAi) {
            fakeRight++;
        } else if (isAiGuess && !isAi) {
            fakeWrong++;
        } else if (!isAiGuess && isAi) {
            fakeWrong++;
        } else {
            realRight++;
        }

        scoreElement.innerText = `Score: ${score}/${totalGuesses}`;

        if (guesses < 30) {
            loadNewImage();
        } else {
            sendResults();
        }
    };

    const sendResults = () => {
        fetch('/send_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                real_right: realRight,
                real_wrong: realWrong,
                fake_right: fakeRight,
                fake_wrong: fakeWrong
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Results sent successfully!');
            }
        });
    };

    aiButton.addEventListener('click', () => checkGuess(true));
    realButton.addEventListener('click', () => checkGuess(false));

    loadNewImage();
});
