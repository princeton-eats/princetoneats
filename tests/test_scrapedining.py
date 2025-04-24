from princetoneats.scrapedining import map_args, get_meal_info, filter_meals


def test_map_args():
    formatted_hall, _, _, _ = map_args("Roma", "4/20/25")
    assert formatted_hall == "+Rockefeller+%26+Mathey+Colleges"


def test_meal_names():
    halls = ["Roma"]
    date = "04/20/25"
    meal_time = "Dinner"
    all_meals = get_meal_info(halls, date, meal_time)

    assert all_meals[0]["name"] == "Chef's Choice Soup of the Day"
    assert all_meals[1]["name"] == "Roma House Beef Vegetable Soup"
    assert all_meals[2]["name"] == "Herb Roasted Chicken"
    assert all_meals[3]["name"] == "Lentil Stew"
    assert all_meals[4]["name"] == "Herbed Rice Pilaf"
    assert all_meals[5]["name"] == "Spicy Fresh Green Beans"


def test_vegetarian():
    halls = ["Roma"]
    date = "04/20/25"
    meal_time = "Dinner"
    all_meals = get_meal_info(halls, date, meal_time)

    # vegetarian
    meals = filter_meals(all_meals, ["vegan-vegetarian"])
    assert len(meals) == 1


def test_halal():
    halls = ["WB"]
    date = "04/20/25"
    meal_time = "Dinner"
    all_meals = get_meal_info(halls, date, meal_time)

    # vegetarian
    meals = filter_meals(all_meals, ["halal"])
    assert len(meals) == 6
