document.addEventListener("DOMContentLoaded", function () {
    setupNavigation();
    handleMealPreferences();
    displayFilteredMeals();
});

function setupNavigation() {
    const menuToggle = document.getElementById("menu-toggle");
    const navLinks = document.getElementById("nav-links");

    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", function () {
            navLinks.classList.toggle("show");
        });
    }
}

function handleMealPreferences() {
    const enterButton = document.getElementById("enterButton"); // Ensure the button exists

    if (enterButton) {
        enterButton.addEventListener("click", function (event) {
            event.preventDefault(); // Prevents any default button behavior

            let selectedFilters = [];
            let checkboxes = document.querySelectorAll('input[name="filter"]:checked');

            checkboxes.forEach((checkbox) => {
                selectedFilters.push(checkbox.value);
            });

            // Save preferences in localStorage
            localStorage.setItem("mealFilters", JSON.stringify(selectedFilters));

            console.log("Redirecting to meals_list.html with filters:", selectedFilters); // Debugging

            // Redirect to meals_list.html
            window.location.href = "meals_list.html";
        });
    }
}

function displayFilteredMeals() {
    let mealResultsDiv = document.getElementById("mealResults");

    if (mealResultsDiv) {
        let filters = JSON.parse(localStorage.getItem("mealFilters")) || [];

        let meals = [
            { name: "Yeh Halal Grilled Chicken", tags: ["halal"] },
            { name: "Whitman Vegetarian Pasta", tags: ["vegetarian"] },
            { name: "Forbes Vegan Salad", tags: ["vegan"] },
            { name: "Rocky Gluten-Free Rice Bowl", tags: ["gluten-free"] },
            { name: "Butler Dairy-Free Smoothie", tags: ["dairy-free"] },
            { name: "Mathey Peanut-Free Sandwich", tags: ["peanut-free"] }
        ];

        let filteredMeals = meals.filter(meal => filters.some(f => meal.tags.includes(f)));

        mealResultsDiv.innerHTML = "";
        if (filteredMeals.length > 0) {
            filteredMeals.forEach(meal => {
                let mealItem = document.createElement("p");
                mealItem.textContent = meal.name;
                mealResultsDiv.appendChild(mealItem);
            });
        } else {
            mealResultsDiv.innerHTML = "<p>No meals found based on your preferences.</p>";
        }
    }
}
