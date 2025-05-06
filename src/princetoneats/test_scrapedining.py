import asyncio
import pytest
import princetoneats.scrapedining as scrapedining


@pytest.mark.parametrize(
    "hall,expected_hall_url,expected_location_num,expected_dhall_name",
    [
        ("roma", "+Rockefeller+%26+Mathey+Colleges", 1, "Rocky & Mathey"),
        ("f", "Forbes+College", 3, "Forbes College"),
        ("wb", "Whitman+College+%26+Butler+College", 8, "Whitman & Butler"),
    ],
)
def test_map_args_todays_date(
    hall, expected_hall_url, expected_location_num, expected_dhall_name
):
    hall_url, _, location_num, dhall_name = scrapedining.map_args(hall, None)
    assert hall_url == expected_hall_url
    assert location_num == expected_location_num
    assert dhall_name == expected_dhall_name


def test_map_args_with_date():
    hall_url, date_url, location_num, dhall_name = scrapedining.map_args(
        "yn", "2023-05-01"
    )
    assert hall_url == "Yeh+College+%26+New+College+West"
    assert date_url == "05%2F01%2F2023"
    assert location_num == 6
    assert dhall_name == "Yeh & NCW"


def test_map_args_invalid_hall():
    with pytest.raises(ValueError):
        scrapedining.map_args("invalid", None)


@pytest.mark.parametrize(
    "ingredients,allergens,expected_tags,unexpected_tags",
    [
        (
            ["Tomato", "Lettuce", "Cucumber"],
            ["None"],
            ["halal", "gluten-free", "dairy-free", "peanut-free"],
            [],
        ),
        (
            ["Chicken", "Rice", "Vegetables"],
            ["None"],
            ["halal", "gluten-free", "dairy-free", "peanut-free"],
            [],
        ),
        (
            ["Pork", "Rice", "Vegetables"],
            ["None"],
            ["gluten-free", "dairy-free", "peanut-free"],
            ["halal"],
        ),
        (
            ["Wheat", "Pasta", "Tomato Sauce"],
            ["Wheat"],
            ["halal", "dairy-free", "peanut-free"],
            ["gluten-free"],
        ),
        (
            ["Milk", "Cheese", "Pasta"],
            ["Milk"],
            ["halal", "peanut-free"],
            ["dairy-free"],
        ),
        (
            ["Chicken", "Rice", "Peanut Sauce"],
            ["Peanuts"],
            ["halal", "gluten-free", "dairy-free"],
            ["peanut-free"],
        ),
    ],
)
def test_get_dietary_tags(ingredients, allergens, expected_tags, unexpected_tags):
    tags = scrapedining.get_dietary_tags(ingredients, allergens)

    # Check all expected tags are present
    for tag in expected_tags:
        assert tag in tags

    # Check all unexpected tags are absent
    for tag in unexpected_tags:
        assert tag not in tags


def test_filter_meals_single_tag():
    meals = [
        {"name": "Meal1", "dietary_tags": ["halal", "gluten-free"]},
        {"name": "Meal2", "dietary_tags": ["dairy-free"]},
        {"name": "Meal3", "dietary_tags": ["halal", "peanut-free"]},
    ]
    filtered = scrapedining.filter_meals(meals, ["halal"])
    assert len(filtered) == 2
    assert filtered[0]["name"] == "Meal1"
    assert filtered[1]["name"] == "Meal3"


def test_filter_meals_multiple_tags():
    meals = [
        {"name": "Meal1", "dietary_tags": ["halal", "gluten-free", "peanut-free"]},
        {"name": "Meal2", "dietary_tags": ["dairy-free", "gluten-free"]},
        {"name": "Meal3", "dietary_tags": ["halal", "peanut-free"]},
    ]
    filtered = scrapedining.filter_meals(meals, ["halal", "gluten-free"])
    assert len(filtered) == 1
    assert filtered[0]["name"] == "Meal1"


def test_filter_meals_no_matches():
    meals = [
        {"name": "Meal1", "dietary_tags": ["halal", "gluten-free"]},
        {"name": "Meal2", "dietary_tags": ["dairy-free"]},
        {"name": "Meal3", "dietary_tags": ["halal", "peanut-free"]},
    ]
    filtered = scrapedining.filter_meals(meals, ["vegan-vegetarian"])
    assert len(filtered) == 0


def test_get_meal_info():
    meals = asyncio.run(scrapedining.get_meal_info(["roma"], None, "Lunch"))
    assert len(meals) > 0
    for meal in meals:
        assert "dhall" in meal
        assert "name" in meal
        assert "ingredients" in meal
        assert "allergens" in meal
        assert "dietary_tags" in meal
        assert "ingredients_string" in meal
        assert "allergens_string" in meal
