# Created by Yusuf, Adham, Ndongo, Achilles, Akuei

import argparse
import requests
from bs4 import BeautifulSoup
import time

# Base URL for ingredient and allergen details
ingredients_page_start = "https://menus.princeton.edu/dining/_Foodpro/online-menu/"


def map_args(hall, date):
    """Map dining hall short names and format date for URL"""
    if hall == "r" or hall == "rocky":
        hall_url = "+Rockefeller+%26+Mathey+Colleges"
    elif hall == "f" or hall == "forbes":
        hall_url = "Forbes+College"
    elif hall == "w" or hall == "whitman":
        hall_url = "Whitman+College+%26+Butler+College"
    elif hall == "y" or hall == "yeh":
        hall_url = "Yeh+College+%26+New+College+West"
    else:
        raise ValueError("Invalid hall name. Use r, f, w, or y.")

    date_url = "%2F".join(date.split("/"))  # e.g., "03/27/2025" → "03%2F27%2F2025"

    return hall_url, date_url


def get_ingredients_and_allergens(url):
    """Scrape both ingredients and allergens from a meal's detail page, filtering out default disclaimers."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        all_text = soup.get_text()

        ingredients = "No ingredients found"
        allergens = "No allergens listed"

        if "INGREDIENTS:" in all_text.upper():
            ingredient_section = all_text.split("INGREDIENTS:", 1)[1]
            if "ALLERGENS:" in ingredient_section.upper():
                ingredient_section, allergen_section = ingredient_section.split(
                    "ALLERGENS:", 1
                )
                ingredients = ingredient_section.strip()
                allergens_raw = allergen_section.strip().split("\n")[0]

                # Filter out Princeton Dining's default disclaimer
                if "committed to providing" in allergens_raw.lower():
                    allergens = "No allergens listed"
                else:
                    allergens = allergens_raw
            else:
                ingredients = ingredient_section.strip()

        return ingredients, allergens

    except Exception as e:
        return f"Error retrieving ingredients: {e}", ""


def scrape_divs(url, class_name):
    """Scrape menu items and display ingredients and allergen info"""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.find_all("div", class_=class_name)

        for div in divs:
            meal_name = div.get_text(strip=True)
            print(f"\n{meal_name}")

            ingredient_links = []
            for a_tag in div.find_all("a", href=True):
                ingredient_link = ingredients_page_start + a_tag["href"]
                ingredient_links.append(ingredient_link)

            for i, link in enumerate(ingredient_links):
                print(f"  Source {i+1}: {link}")
                time.sleep(0.5)  # Be kind to the server

                ingredients, allergens = get_ingredients_and_allergens(link)
                print(f"  Ingredients: {ingredients}")
                print(f"  Allergens: {allergens}\n")

    except Exception as e:
        print(f"Error during scraping: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape menu items, ingredients, and allergens from Princeton Dining"
    )
    parser.add_argument("--hall", required=True, help="Dining hall (r, f, w, y)")
    parser.add_argument("--meal", required=True, help="Meal (Breakfast, Lunch, Dinner)")
    parser.add_argument("--date", required=True, help="Date in format MM/DD/YYYY")

    args = parser.parse_args()

    hall_url, date_url = map_args(args.hall, args.date)

    url = f"https://menus.princeton.edu/dining/_Foodpro/online-menu/pickMenu.asp?locationNum=01&locationName={hall_url}&dtdate={date_url}&mealName={args.meal}&sName=Princeton+University+Campus+Dining"
    class_name = "pickmenucoldispname"

    print(f"\nFetching {args.meal} menu for {args.hall} on {args.date}...\n")
    scrape_divs(url, class_name)
