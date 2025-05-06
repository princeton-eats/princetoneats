# OUTDATED TESTS

# def test_map_args():
#     formatted_hall, _, _, _ = map_args("Roma", "4/20/25")
#     assert formatted_hall == "+Rockefeller+%26+Mathey+Colleges"


# def test_meal_names():
#     halls = ["Roma"]
#     date = "04/20/25"
#     meal_time = "Dinner"
#     all_meals = asyncio.run(get_meal_info(halls, date, meal_time))
#     names = list(meal["name"] for meal in all_meals)

#     assert "Chef's Choice Soup of the Day" in names
#     assert "Roma House Beef Vegetable Soup" in names
#     assert "Herb Roasted Chicken" in names
#     assert "Lentil Stew" in names
#     assert "Herbed Rice Pilaf" in names
#     assert "Spicy Fresh Green Beans" in names


# def test_vegetarian():
#     halls = ["Roma"]
#     date = "04/20/25"
#     meal_time = "Dinner"
#     all_meals = asyncio.run(get_meal_info(halls, date, meal_time))

#     # vegetarian
#     meals = filter_meals(all_meals, ["vegan-vegetarian"])
#     assert len(meals) == 1


# def test_halal():
#     halls = ["WB"]
#     date = "04/20/25"
#     meal_time = "Dinner"
#     all_meals = asyncio.run(get_meal_info(halls, date, meal_time))

#     # vegetarian
#     meals = filter_meals(all_meals, ["halal"])
#     assert len(meals) == 6
