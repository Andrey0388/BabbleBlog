function search() {
    var searchText = document.getElementById('searchInput').value.toLowerCase();
    var elements = document.querySelectorAll('*');

    elements.forEach(function(element) {
        var originalHTML = element.innerHTML; // Сохраняем исходное содержимое элемента
        var innerHTML = originalHTML.toLowerCase();
        var index = innerHTML.indexOf(searchText);
        while (index !== -1) {
            var leftPart = originalHTML.substring(0, index);
            var highlightedPart = originalHTML.substring(index, index + searchText.length);
            var rightPart = originalHTML.substring(index + searchText.length);
            element.innerHTML = leftPart + '<span class="highlighted">' + highlightedPart + '</span>' + rightPart;
            innerHTML = rightPart.toLowerCase();
            index = innerHTML.indexOf(searchText);
        }
    });
}
