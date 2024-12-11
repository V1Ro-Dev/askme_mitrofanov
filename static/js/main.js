function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const questionLike = () => {
    const cards = document.querySelectorAll('.question-card')
    for (const card of cards){
        const likeButton = card.querySelector('.like-button')
        const likeCounter = card.querySelector('.like-counter')
        const id = card.dataset.id

        likeButton.addEventListener('click', () => {
            const request = new Request(`/questionLike/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    question_id: id
                })
            })
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    likeCounter.innerHTML = data.likes_count;
                    if (data.liked) {
                        likeButton.classList.add('liked');
                    } else {
                        likeButton.classList.remove('liked');
                    }
                })
        })
    }
}

const answerLike = () => {
    const question_id = document.querySelector('.question-card').dataset.id
    const cards = document.querySelectorAll('.answer-card')
    for (const card of cards){
        const likeButton = card.querySelector('.like-button-answer')
        const likeCounter = card.querySelector('.like-counter-answer')
        const id = card.dataset.id

        likeButton.addEventListener('click', () => {
            const request = new Request(`/answerLike/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    question_id: question_id,
                    answer_id: id
                })
            })
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    likeCounter.innerHTML = data.likes_count
                    if (data.liked) {
                        likeButton.classList.add('liked');
                    } else {
                        likeButton.classList.remove('liked');
                    }
                })
        })
    }
}

const correctAnswer = () => {
    const question_id = document.querySelector('.question-card').dataset.id
    const cards = document.querySelectorAll('.answer-card')
    for (const card of cards){
        const correctButton = card.querySelector('.form-check-input')
        const id = card.dataset.id

        correctButton.addEventListener('change', () => {
            const request = new Request(`/correctAnswer/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    question_id: question_id,
                    answer_id: id
                })
            })
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                        correctButton.checked = data.correct;
                })
        })
    }
}

document.addEventListener('DOMContentLoaded', () => {
    questionLike();
    answerLike();
    correctAnswer()
});
