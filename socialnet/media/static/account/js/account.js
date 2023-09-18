
document.addEventListener("DOMContentLoaded", function(event) {
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
});

window.onbeforeunload = function(e) {
    localStorage.setItem('scrollpos', window.scrollY);
};


window.addEventListener('load', function() {
    const submitBtn = document.querySelector('#submitBtn');

    if (submitBtn) { // проверяем, существует ли элемент на странице
        window.addEventListener('scroll', function() {
            if (window.scrollY === 0) { // используем window.scrollY вместо window.pageYOffset
                submitBtn.click();
            }
        });
    }
});




//window.addEventListener('load', function() {
//    const submitBtn = document.querySelector('#submitBtn');
//
//    if (submitBtn) { // проверяем, существует ли элемент на странице
//        window.addEventListener('scroll', function() {
//            if (window.scrollY + window.innerHeight === document.documentElement.scrollHeight) {
//                submitBtn.click();
//            }
//        });
//    }
//});









// Функция для отправки AJAX-запроса на сервер
function checkNewMessages() {
  // Отправка AJAX-запроса на сервер
fetch('/messages/check_new_messages')
    .then(response => response.json())
    .then(data => {
        if (data.unread_count) {
            document.querySelector("#menu-message").innerText = data.unread_count;
            document.querySelector("#menu-message").style.display = "inline-block";

            // Если есть новые сообщения, выполните необходимые действия
            console.log('Новые сообщения:', data.messages);
            // Например, обновите список сообщений на странице
            updateMessageList(data.messages, temp);
        }
    })

    .catch(error => {
        console.error('Ошибка при проверке новых сообщений:', error);
    });
}

// Функция для обновления списка сообщений на странице
function updateMessageList(messages, temp) {


  // Тут можно добавить код для обновления списка сообщений на странице
}

// Запуск проверки каждые 3 секунды
setInterval(checkNewMessages, 3000);
