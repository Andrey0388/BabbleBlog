function search() {
    var searchText = document.getElementById('searchInput').value;
    var elements = document.querySelectorAll('*');

    // Удаляем предыдущую подсветку, если она есть
    removeHighlight();

    elements.forEach(function(element) {
        highlightTextInElement(element, searchText);
    });
}

function highlightTextInElement(element, searchText) {
    if (element.tagName !== 'SCRIPT' && element.tagName !== 'STYLE') {
        element.childNodes.forEach(function(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                var regex = new RegExp('(' + escapeRegExp(searchText) + ')', 'gi');
                var newText = node.textContent.replace(regex, '<span class="highlighted">$1</span>');
                var tempElement = document.createElement('div');
                tempElement.innerHTML = newText;
                while (tempElement.firstChild) {
                    node.parentNode.insertBefore(tempElement.firstChild, node);
                }
                node.parentNode.removeChild(node);
            }
        });
    }
}

function removeHighlight() {
    var highlightedElements = document.querySelectorAll('.highlighted');
    highlightedElements.forEach(function(element) {
        element.outerHTML = element.innerHTML;
    });
}

// Функция для экранирования специальных символов в регулярном выражении
function escapeRegExp(text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
}
