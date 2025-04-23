# Created by Yusuf, Adham, Ndongo, Achilles, Akuei
import argparse
import asyncio
import aiohttp
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime

_MENUS_URL_START = "https://menus.princeton.edu/dining/_Foodpro/online-menu/"
_MEAL_NAME_CLASS = "pickmenucoldispname"
_MEAL_SECTION_CLASS = "pickmenucolmenucat"
_INGREDIENTS_CLASS = "labelingredientsvalue"
_ALLERGENS_CLASS = "labelallergensvalue"


def get_current_date():
    return datetime.now().strftime("%m/%d/%y")


def map_args(hall, date):
    """Format hall & date for URL; return (hall_url, date_url, location_num, dhall_name)."""
    hall = hall.lower()
    if hall in ("r", "roma"):
        hall_url, location_num, dhall_name = (
            "+Rockefeller+%26+Mathey+Colleges",
            1,
            "Rocky & Mathey",
        )
    elif hall in ("f", "forbes"):
        hall_url, location_num, dhall_name = "Forbes+College", 3, "Forbes College"
    elif hall in ("w", "wb"):
        hall_url, location_num, dhall_name = (
            "Whitman+College+%26+Butler+College",
            8,
            "Whitman & Butler",
        )
    elif hall in ("y", "yn"):
        hall_url, location_num, dhall_name = (
            "Yeh+College+%26+New+College+West",
            6,
            "Yeh & NCW",
        )
    elif hall in ("c", "cjl"):
        hall_url, location_num, dhall_name = "Center+for+Jewish+Life", 5, "CJL"
    elif hall in ("g", "grad", "graduate"):
        hall_url, location_num, dhall_name = "Graduate+College", 4, "Graduate College"
    else:
        raise ValueError(f"Unknown hall code: {hall}")

    if date is None:
        date = get_current_date()
    date_url = "%2F".join(date.split("/"))  # MM%2FDD%2FYY

    return hall_url, date_url, location_num, dhall_name


def get_details_url(formatted_hall, formatted_date, meal_time, location_num):
    return (
        f"{_MENUS_URL_START}pickMenu.asp?"
        f"locationNum=0{location_num}&locationName={formatted_hall}"
        f"&dtdate={formatted_date}&mealName={meal_time}"
        f"&sName=Princeton+University+Campus+Dining"
    )


async def fetch(session, url):
    async with session.get(url, timeout=10) as resp:
        resp.raise_for_status()
        # drop any bytes that can’t be decoded as UTF-8
        return await resp.text(encoding="utf-8", errors="ignore")


async def parse_main_page(session, hall, date, meal_time):
    f_hall, f_date, loc_num, dhall_name = map_args(hall, date)
    main_url = get_details_url(f_hall, f_date, meal_time, loc_num)
    html = await fetch(session, main_url)
    soup = BeautifulSoup(html, "lxml")

    section = None
    jobs = []
    for div in soup.find_all("div", class_=[_MEAL_SECTION_CLASS, _MEAL_NAME_CLASS]):
        cls = div.get("class", [None])[0]
        if cls == _MEAL_SECTION_CLASS:
            section = div.get_text(strip=True).lower()
        else:
            a = div.find("a", href=True)
            if not a:
                continue
            jobs.append(
                {
                    "dhall": dhall_name,
                    "name": div.get_text(strip=True),
                    "section": section,
                    "detail_url": _MENUS_URL_START + a["href"],
                }
            )
    return jobs


async def get_ingredients_and_allergens(session, job):
    """Fetch & parse only the <span> tags for ingredients & allergens."""
    try:
        html = await fetch(session, job["detail_url"])
        spans = SoupStrainer("span")
        soup = BeautifulSoup(html, "lxml", parse_only=spans)

        def extract(cls, none_msg):
            tag = soup.find("span", class_=cls)
            text = tag.get_text() if tag else none_msg
            items = [s.strip() for s in text.split(",") if s.strip()]
            return (items or [none_msg], text.strip() or none_msg)

        ingredients, ing_str = extract(_INGREDIENTS_CLASS, "No ingredients found")
        allergens, all_str = extract(_ALLERGENS_CLASS, "No allergens listed")
        return job, ingredients, allergens, ing_str, all_str

    except Exception as e:
        return job, ["Error retrieving ingredients: " + str(e)], [], "", ""


def get_dietary_tags(ingredients, allergens):
    """Return dietary tags based on ingredients & allergens lists."""
    tags = []
    ing_lower = [i.lower() for i in ingredients]
    all_lower = [a.lower() for a in allergens]

    # Halal: no pork, bacon, etc.
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

    # Gluten-free
    if not any(
        grain in (ing + " " + al)
        for grain in ["wheat", "gluten", "barley", "rye", "malt", "semolina"]
        for ing in ing_lower
        for al in all_lower
    ):
        tags.append("gluten-free")

    # Dairy-free
    if not any(
        dairy in (ing + " " + al)
        for dairy in ["milk", "cheese", "butter", "cream", "yogurt", "casein", "whey"]
        for ing in ing_lower
        for al in all_lower
    ):
        tags.append("dairy-free")

    # Peanut-free
    if not any("peanut" in a for a in all_lower):
        tags.append("peanut-free")

    return tags


async def get_meal_info(halls, date, meal_time, concurrency=20):
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        # 1) build list of all detail-page jobs
        main_tasks = [parse_main_page(session, h, date, meal_time) for h in halls]
        all_jobs = [job for sub in await asyncio.gather(*main_tasks) for job in sub]

        # 2) fetch and parse all detail pages in parallel
        detail_tasks = [get_ingredients_and_allergens(session, job) for job in all_jobs]
        meals = []
        for coro in asyncio.as_completed(detail_tasks):
            job, ing, al, ing_str, all_str = await coro
            tags = get_dietary_tags(ing, al)
            if (
                "vegetarian" in (job["section"] or "")
                and "vegan-vegetarian" not in tags
            ):
                tags.append("vegan-vegetarian")
            meals.append(
                {
                    "dhall": job["dhall"],
                    "name": job["name"],
                    "ingredients": ing,
                    "allergens": al,
                    "dietary_tags": tags,
                    "ingredients_string": ing_str,
                    "allergens_string": all_str,
                }
            )
        return meals


def filter_meals(meals, tags):
    """Return only those meals containing all specified tags."""
    return [m for m in meals if all(tag in m["dietary_tags"] for tag in tags)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hall", required=True, help="Comma-separated hall codes (e.g. r,f,w)"
    )
    parser.add_argument("--mealtime", required=True)
    parser.add_argument("--date", help="MM/DD/YY (defaults to today)")
    parser.add_argument("--filter", help="Dietary tag to filter by")
    args = parser.parse_args()

    halls = [h.strip() for h in args.hall.split(",") if h.strip()]
    meals = asyncio.run(get_meal_info(halls, args.date, args.mealtime))

    if args.filter:
        meals = filter_meals(meals, [args.filter.lower()])

    for m in meals:
        print(m["name"])
        print("Ingredients:", ", ".join(m["ingredients"]))
        print("Allergens:", ", ".join(m["allergens"]))
        print("Tags:", ", ".join(m["dietary_tags"]))
        print()
