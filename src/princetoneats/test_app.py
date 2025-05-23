import pytest
import princetoneats.app as app
from unittest.mock import patch


@pytest.fixture
def client():
    app.app.testing = True
    with app.app.test_client() as client:
        yield client


@pytest.fixture
def authenticated_client():
    app.app.testing = True
    with app.app.test_client() as client:
        with client.session_transaction() as session:
            session["user_info"] = {
                "user": "testuser",
                "attributes": {"displayname": ["Test User"]},
            }
        yield client


def test_home_page_unauthenticated(client):
    response = client.get("/")
    assert response.status_code == 200


@patch("princetoneats.auth.is_authenticated")
def test_home_page_authenticated(mock_auth, authenticated_client):
    mock_auth.return_value = True
    response = authenticated_client.get("/")
    assert response.status_code == 302  # Redirect to dashboard


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200


@patch("princetoneats.auth.is_authenticated")
def test_dashboard_unauthenticated(mock_auth, client):
    mock_auth.return_value = False
    response = client.get("/dashboard")
    assert response.status_code == 302  # Redirect to home


@patch("princetoneats.database.get_user_info")
@patch("princetoneats.scrapedining.get_meal_info")
def test_dashboard_authenticated(
    mock_get_meal_info, mock_get_user_info, authenticated_client
):
    # Mock database response
    mock_get_user_info.return_value = {
        "fav_meals": "Test Meal",
        "preferences": {
            "vegan-vegetarian": True,
            "halal": False,
            "gluten-free": True,
            "dairy-free": False,
            "peanut-free": True,
        },
    }

    mock_get_meal_info.return_value = [
        {
            "dhall": "Roma",
            "name": "Test Meal 1",
            "ingredients": ["Ingredient1", "Ingredient2"],
            "allergens": ["None"],
            "dietary_tags": ["vegan-vegetarian", "gluten-free", "peanut-free"],
        },
        {
            "dhall": "Roma",
            "name": "Test Meal 2",
            "ingredients": ["Ingredient1", "Ingredient2"],
            "allergens": ["None"],
            "dietary_tags": ["vegan-vegetarian", "gluten-free", "peanut-free"],
        },
        {
            "dhall": "Roma",
            "name": "Test Meal 3",
            "ingredients": ["Ingredient1", "Ingredient2"],
            "allergens": ["None"],
            "dietary_tags": ["vegan-vegetarian", "gluten-free", "peanut-free"],
        },
    ]

    response = authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert "Roma" in response.text


def test_find_meals_page(client):
    response = client.get("/find_meals")
    assert response.status_code == 200
    assert '"vegan-vegetarian" >' in response.text
    assert '"halal" >' in response.text
    assert '"gluten-free" >' in response.text
    assert '"dairy-free" >' in response.text
    assert '"peanut-free" >' in response.text


@patch("princetoneats.database.get_user_info")
def test_find_meals_authenticated(mock_get_user_info, authenticated_client):
    # Mock database response
    mock_get_user_info.return_value = {
        "preferences": {
            "vegan-vegetarian": True,
            "halal": False,
            "gluten-free": True,
            "dairy-free": False,
            "peanut-free": True,
        }
    }

    response = authenticated_client.get("/find_meals")
    assert response.status_code == 200
    # check that only the true values are set to checked in the form
    assert '"vegan-vegetarian" checked>' in response.text
    assert '"halal" >' in response.text
    assert '"gluten-free" checked>' in response.text
    assert '"dairy-free" >' in response.text
    assert '"peanut-free" checked>' in response.text


@patch("princetoneats.scrapedining.get_meal_info")
@patch("princetoneats.scrapedining.filter_meals")
def test_meals_list(mock_filter_meals, mock_get_meal_info, client):
    meals = [
        {
            "dhall": "Roma",
            "name": "Test Meal 1",
            "ingredients": ["Ingredient1", "Ingredient2"],
            "allergens": ["None"],
            "dietary_tags": ["vegan-vegetarian", "gluten-free"],
        },
        {
            "dhall": "Forbes",
            "name": "Test Meal 2",
            "ingredients": ["Ingredient3", "Ingredient4"],
            "allergens": ["Dairy"],
            "dietary_tags": ["halal", "peanut-free"],
        },
    ]
    mock_get_meal_info.return_value = meals
    mock_filter_meals.return_value = [meals[0]]

    response = client.get(
        "/meals_list?DHfilter=Roma&MTfilter=Lunch&ARfilter=vegan-vegetarian&date=2023-05-01"
    )
    assert response.status_code == 200
    # filter must capture the roma meal and not the forbes meal
    assert "Roma" in response.text
    assert "Forbes" not in response.text


@patch("princetoneats.auth.is_authenticated")
@patch("princetoneats.database.add_fav_meal")
def test_updatefav_add(mock_add_fav_meal, mock_is_authenticated, authenticated_client):
    # Mock authentication
    mock_is_authenticated.return_value = True

    response = authenticated_client.get("/updatefav?name=Test%20Meal&fav=false")
    assert response.status_code == 200
    mock_add_fav_meal.assert_called_once()


@patch("princetoneats.auth.is_authenticated")
@patch("princetoneats.database.remove_fav_meal")
def test_updatefav_remove(
    mock_remove_fav_meal, mock_is_authenticated, authenticated_client
):
    # Mock authentication
    mock_is_authenticated.return_value = True

    response = authenticated_client.get("/updatefav?name=Test%20Meal&fav=true")
    assert response.status_code == 200
    mock_remove_fav_meal.assert_called_once()


@patch("princetoneats.auth.is_authenticated")
def test_updatefav_unauthenticated(mock_is_authenticated, client):
    # Mock authentication
    mock_is_authenticated.return_value = False

    response = client.get("/updatefav?name=Test%20Meal&fav=false")
    # Response should report server error
    assert response.status_code == 500
