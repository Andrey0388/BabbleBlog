document.addEventListener('DOMContentLoaded', function() {
    // Получаем все кнопки "Нравится" и "Отменить"
    var likeButtons = document.querySelectorAll('.like-btn');

    // Добавляем обработчик событий для каждой кнопки
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var newsId = button.dataset.newsId;
            var action = button.dataset.action;

            // Отправляем AJAX-запрос на сервер
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/toggle_like', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        // Обновляем количество лайков и текст кнопки
                        var likesCountElement = document.querySelector('.likes-count[data-news-id="' + newsId + '"]');
                        var currentLikes = parseInt(likesCountElement.innerText);
                        if (action === 'like') {
                            likesCountElement.innerText = currentLikes + 1;
                            button.dataset.action = 'unlike';
                            button.innerText = 'Отменить';
                        } else {
                            likesCountElement.innerText = currentLikes - 1;
                            button.dataset.action = 'like';
                            button.innerText = 'Нравится';
                        }
                    } else {
                        // В случае ошибки вы можете добавить обработку здесь
                        console.error('Ошибка при выполнении запроса');
                    }
                }
            };

            // Отправляем JSON-данные с идентификатором новости и действием
            var data = JSON.stringify({'news_id': newsId});
            xhr.send(data);
        });
    });
});

