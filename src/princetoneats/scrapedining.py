# Created by Yusuf, Adham, Ndongo, Achilles, Akuei
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

ingredients_page_start = "https://menus.princeton.edu/dining/_Foodpro/online-menu/"


def get_current_date():
    return datetime.now().strftime("%m/%d/%y")


def map_args(hall, date):
    if hall == "r" or hall == "rocky":
        hall_url = "+Rockefeller+%26+Mathey+Colleges"
    elif hall == "f" or hall == "forbes":
        hall_url = "Forbes+College"
    elif hall == "w" or hall == "whitman":
        hall_url = "Whitman+College+%26+Butler+College"
    elif hall == "y" or hall == "yeh":
        hall_url = "Yeh+College+%26+New+College+West"

    if date is None:
        date_url = get_current_date()
    else:
        date_url = "%2F".join(date.split("/"))

    return hall_url, date_url


def scrape_divs(url, class_name):
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
        print(div.get_text(strip=True), end=" ")
        # Find all <a> tags within the div and print their href attribute
        # for a_tag in div.find_all("a", href=True):
        #     print(ingredients_page_start + a_tag["href"])
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape divs from a website")
    parser.add_argument("--hall", required=True, help="Specify the hall")
    parser.add_argument("--meal", required=True, help="Specify which meal of the day")
    parser.add_argument("--date", required=False, help="Specify the date")
    args = parser.parse_args()

    hall_url, date_url = map_args(args.hall, args.date)

    url = f"https://menus.princeton.edu/dining/_Foodpro/online-menu/pickMenu.asp?locationNum=01&locationName={hall_url}&dtdate={date_url}&mealName={args.meal}&sName=Princeton+University+Campus+Dining"
    class_name = "pickmenucoldispname"
    scrape_divs(url, class_name)
