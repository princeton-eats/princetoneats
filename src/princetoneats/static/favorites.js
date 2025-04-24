let request = null;

function toggleIsFav(name) {
   let url = '/updatefav?name=' + name;
   if (request !== null)
         request.abort();
   request = new XMLHttpRequest();
   request.onerror = handleError;
   request.open('GET', url);
   request.send();
}

function handleError() {
   alert('There\'s been an error.');
}
