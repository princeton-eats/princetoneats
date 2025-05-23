let request = null;

function toggleIsFav(name, isCurrentFavorite) {
   console.log('toggling in database for:', name);
   const url = '/updatefav?name=' + encodeURIComponent(name) + '&fav=' + isCurrentFavorite;

   // Create a new request without aborting previous ones
   const xhr = new XMLHttpRequest();

   xhr.onload = function() {
      console.log('done updating database for:', name);
   };

   xhr.onerror = function(error) {
      alert('Error updating favorite status for:', name, error);
   };

   xhr.open('GET', url);
   xhr.send();
}

document.addEventListener('click', function(event) {
   // Handle isfavorite buttons
   if (event.target.closest('.isfavorite')) {
      const heart = event.target.closest('.isfavorite');
      console.log('save as not favorite');

      heart.className = 'notfavorite';
      heart.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='25' height='25' fill='currentColor' class='bi bi-heart' viewBox='0 0 16 16'>\
                        <path d='m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15'/>\
                     </svg>";
   }

   // Handle notfavorite buttons
   if (event.target.closest('.notfavorite')) {
      const heart = event.target.closest('.notfavorite');
      console.log('save as favorite');
      heart.className = 'isfavorite';
      heart.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='25' height='25' fill='currentColor' class='bi bi-heart-fill' viewBox='0 0 16 16'>\
                        <path fill-rule='evenodd' d='M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314'/>\
                     </svg>";
   }
});
