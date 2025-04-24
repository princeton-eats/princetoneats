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

const buttons = document.querySelectorAll('.favorites');

// Add event listener to each button
buttons.forEach(button => {
   button.addEventListener('click', function() {
      // Check current text and toggle accordingly
      if (this.textContent.includes("Add")) {
         this.textContent = "Remove Favorite";
      } else if (this.textContent.includes("Remove")) {
         this.textContent = "Add Favorite";
      }
   });
});
