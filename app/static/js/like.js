console.log("Like script loaded successfully.");

document.addEventListener('DOMContentLoaded', function() {
    var likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Проверяем, активна ли кнопка
            if (!button.disabled) {
                // Выполняем действие при нажатии на активную кнопку (лайк)
                alert('Лайк поставлен!');
            }
        });
    });
});
