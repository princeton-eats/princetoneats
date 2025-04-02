# Created by Yusuf, Adham, Ndongo, Achilles, Akuei
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

ingredients_page_start = "https://menus.princeton.edu/dining/_Foodpro/online-menu/"
class_name = "pickmenucoldispname"


def get_current_date():
    return datetime.now().strftime("%m/%d/%y")


def map_args(hall, date):
    if hall == "r" or hall == "Roma":
        hall_url = "+Rockefeller+%26+Mathey+Colleges"
    elif hall == "f" or hall == "Forbes":
        hall_url = "Forbes+College"
    elif hall == "w" or hall == "WB":
        hall_url = "Whitman+College+%26+Butler+College"
    elif hall == "y" or hall == "YN":
        hall_url = "Yeh+College+%26+New+College+West"

    if date is None:
        date_url = get_current_date()
    else:
        date_url = "%2F".join(date.split("/"))

    return hall_url, date_url


def get_details_url(hall, date, meal):
    return f"https://menus.princeton.edu/dining/_Foodpro/online-menu/pickMenu.asp?locationNum=01&locationName={hall}&dtdate={date}&mealName={meal}&sName=Princeton+University+Campus+Dining"
    # meal, use capital first letter
    # no unneded 0's in date


def get_meal_names(halls, date, meal):
    names = []
    for hall in halls:
        # temporary: to separate dhalls
        names.append("--" + hall + "--")
        formatted_hall, formatted_date = map_args(hall, date)
        # meal doesn't need formatting
        url = get_details_url(formatted_hall, formatted_date, meal)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to retrieve page, status code: {response.status_code}")
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all divs with the given class
        divs = soup.find_all("div", class_=class_name)

        # Print the HTML content of each div
        for div in divs:
            names.append(div.get_text(strip=True))
            # Find all <a> tags within the div and print their href attribute
            # for a_tag in div.find_all("a", href=True):
            #     print(ingredients_page_start + a_tag["href"])

    return names


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape divs from a website")
    parser.add_argument("--hall", required=True, help="Specify the hall")
    parser.add_argument("--meal", required=True, help="Specify which meal of the day")
    parser.add_argument("--date", required=False, help="Specify the date")
    args = parser.parse_args()

    for name in get_meal_names(args.hall, args.date, args.meal):
        print(name)
