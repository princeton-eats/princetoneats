# Created by Yusuf, Adham, Ndongo, Achilles, Akuei
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

_MENUS_URL_START = "https://menus.princeton.edu/dining/_Foodpro/online-menu/"
_MEAL_NAME_CLASS = "pickmenucoldispname"
_INGREDIENTS_CLASS = "labelingredientsvalue"
_ALLERGENS_CLASS = "labelallergensvalue"


def get_current_date():
    return datetime.now().strftime("%m/%d/%y")


def map_args(hall, date):
    """Format the hall and date for the URL, and also return
    the unique location number for this dining hall"""
    if hall == "r" or hall == "Roma":
        hall_url = "+Rockefeller+%26+Mathey+Colleges"
        location_num = 1
        dhall_name = "Rocky & Mathey"
    elif hall == "f" or hall == "Forbes":
        hall_url = "Forbes+College"
        location_num = 3
        dhall_name = "Forbes College"
    elif hall == "w" or hall == "WB":
        hall_url = "Whitman+College+%26+Butler+College"
        location_num = 8
        dhall_name = "Whitman & Butler"
    elif hall == "y" or hall == "YN":
        hall_url = "Yeh+College+%26+New+College+West"
        location_num = 6
        dhall_name = "Yeh & NCW"
    elif hall == "c" or hall == "CJL":
        hall_url = "Center+for+Jewish+Life"
        location_num = 5
        dhall_name = "CJL"
    elif hall == "g" or hall == "Grad":
        hall_url = "Graduate+College"
        location_num = 4
        dhall_name = "Graduate College"

    if date is None:
        date = get_current_date()
    date_url = "%2F".join(date.split("/"))

    return hall_url, date_url, location_num, dhall_name


def get_details_url(formatted_hall, formatted_date, formatted_meal, location_num):
    """Generate the Dining Menus URL for the page with this information.
    Requires inputs to be formatted to their URL equivalent."""
    return f"https://menus.princeton.edu/dining/_Foodpro/online-menu/pickMenu.asp?locationNum=0{location_num}&locationName={formatted_hall}&dtdate={formatted_date}&mealName={formatted_meal}&sName=Princeton+University+Campus+Dining"


def get_ingredients_and_allergens(url):
    """Scrape both ingredients and allergens from a meal's detail page, filtering
    out default disclaimers."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        ingredients_span = soup.find("span", class_=_INGREDIENTS_CLASS)
        ingredients = ingredients_span.get_text().split(",")
        if len(ingredients) == 0:
            ingredients = ["No ingredients found"]

        allergens_span = soup.find("span", class_=_ALLERGENS_CLASS)
        allergens = allergens_span.get_text().split(",")
        if len(allergens[0]) == 0:
            allergens[0] = ["No allergens listed"]

        return ingredients, allergens

    except Exception as e:
        return f"Error retrieving ingredients: {e}", ""


def get_meal_info(halls, date, meal_time):
    """Return a list of dictionaries containing meal information. Each meal
    consists of {'dhall':, 'name': , 'ingredients:', 'allergens:', 'dietary_tags:'}."""
    meals = []
    for hall in halls:
        formatted_hall, formatted_date, location_num, dhall_name = map_args(hall, date)

        # meal doesn't need formatting
        url = get_details_url(formatted_hall, formatted_date, meal_time, location_num)

        response = requests.get(url)

        if response.status_code != 200:
            print(
                f"Failed to retrieve page for {hall}, status code: {response.status_code}"
            )
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all divs with the meal names.
        divs = soup.find_all("div", class_=_MEAL_NAME_CLASS)

        for div in divs:
            name = div.get_text(strip=True)
            # Find all <a> tags within the divs and print their href attribute
            a_tag = div.find("a", href=True)
            details_url = _MENUS_URL_START + a_tag["href"]

            ingredients, allergens = get_ingredients_and_allergens(details_url)

            tags = get_dietary_tags(ingredients, allergens)

            meals.append(
                {
                    "dhall": dhall_name,
                    "name": name,
                    "ingredients": ingredients,
                    "allergens": allergens,
                    "dietary_tags": tags,
                }
            )

    return meals


def get_dietary_tags(ingredients, allergens):
    """Return a list of tags that these ingredients and allergens satisfy"""

    tags = []

    ing_lower = [i.lower() for i in ingredients]
    all_lower = [a.lower() for a in allergens]

    if not any(
        haram in ing
        for haram in [
            "pork",
            "bacon",
            "ham",
            "lard",
            "alcohol",
            "beer",
            "wine",
            "gelatin",
        ]
        for ing in ing_lower
    ):
        tags.append("halal")

    if not any(
        gluten in ing + " " + al
        for gluten in ["wheat", "gluten", "barley", "rye", "malt", "semolina"]
        for ing in ing_lower
        for al in all_lower
    ):
        tags.append("gluten-free")

    if not any(
        dairy in ing + " " + al
        for dairy in ["milk", "cheese", "butter", "cream", "yogurt", "casein", "whey"]
        for ing in ing_lower
        for al in all_lower
    ):
        tags.append("dairy-free")

    if not any("peanut" in a for a in all_lower):
        tags.append("peanut-free")

    # TODO: get vegan/vegetarian to work
    # temporarily mark everything vegan-vegetarian, effectively ignoring this restriction
    tags.append("vegan-vegetarian")

    return tags


def filter_meals(meals, tags):
    """Returns a list of meals that have all of the given tags"""

    return list(
        meal for meal in meals if all(tag in meal["dietary_tags"] for tag in tags)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape divs from a website")
    parser.add_argument("--hall", required=True, help="Specify the hall")
    parser.add_argument(
        "--mealtime", required=True, help="Specify which meal of the day"
    )
    parser.add_argument("--date", required=False, help="Specify the date")
    parser.add_argument(
        "--filter", required=False, help="Filter (e.g. Vegan, Halal, etc.)"
    )
    args = parser.parse_args()

    meals = get_meal_info(args.hall, args.date, args.mealtime)

    if args.filter:
        meals = filter_meals(meals, [args.filter])

    for info in meals:
        print(info["name"])
        print("Ingredients:", ", ".join(info["ingredients"]))
        print("Allergens:", ", ".join(info["allergens"]))
        print()
