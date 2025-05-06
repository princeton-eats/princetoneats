import pytest
import princetoneats.database as database
import sqlalchemy
import sqlalchemy.orm


# Fixture for database session
@pytest.fixture
def db_session():
    # Create a temporary database file
    import tempfile
    import os

    # Create temporary file path
    temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_file.close()
    temp_db_path = temp_db_file.name

    # Set up test database
    engine = sqlalchemy.create_engine(f"sqlite:///{temp_db_path}")
    session = sqlalchemy.orm.Session(engine)

    # Create all tables
    database.Base.metadata.create_all(engine)

    # Mock the database functions to use our test session
    original_engine = database.engine
    database.engine = engine

    # Provide the session to the test
    yield session

    # Teardown
    database.engine = original_engine
    session.close()
    engine.dispose()

    # Remove the temporary database file
    os.unlink(temp_db_path)


def test_add_user(db_session):
    # Test adding a new user
    user = database.add_user("testuser", db_session)
    assert user.username == "testuser"
    assert user.fav_meals == ""
    assert not user.veg
    assert not user.halal
    assert not user.glutenfree
    assert not user.dairyfree
    assert not user.peanutfree


def test_set_user_prefs_new_user(db_session):
    # Test setting preferences for a new user
    result = database.set_user_prefs("newuser", True, False, True, False, True)
    assert result["preferences"]["vegan-vegetarian"] is True
    assert result["preferences"]["halal"] is False
    assert result["preferences"]["gluten-free"] is True
    assert result["preferences"]["dairy-free"] is False
    assert result["preferences"]["peanut-free"] is True


def test_set_user_prefs_existing_user(db_session):
    # Add user first
    database.add_user("existinguser", db_session)

    # Test updating preferences
    result = database.set_user_prefs("existinguser", True, True, False, False, False)
    assert result["preferences"]["vegan-vegetarian"] is True
    assert result["preferences"]["halal"] is True
    assert result["preferences"]["gluten-free"] is False

    # Update again
    result = database.set_user_prefs("existinguser", False, True, True, True, False)
    assert result["preferences"]["vegan-vegetarian"] is False
    assert result["preferences"]["gluten-free"] is True
    assert result["preferences"]["dairy-free"] is True


def test_get_user_info_existing_user(db_session):
    # Add user with preferences
    database.add_user("infouser", db_session)
    database.set_user_prefs("infouser", True, False, True, False, True)
    database.add_fav_meal("infouser", "Chicken")
    database.add_fav_meal("infouser", "Cheese")

    # Test getting info
    result = database.get_user_info("infouser")
    assert result["fav_meals"] == ",Chicken,Cheese"
    assert result["preferences"]["vegan-vegetarian"] is True
    assert result["preferences"]["halal"] is False
    assert result["preferences"]["gluten-free"] is True


def test_get_user_info_nonexistent_user(db_session):
    # Test getting info for non-existent user
    result = database.get_user_info("nonexistentuser")
    assert result["fav_meals"] == ""
    assert result["preferences"]["vegan-vegetarian"] is False
    assert result["preferences"]["halal"] is False
    assert result["preferences"]["gluten-free"] is False
    assert result["preferences"]["dairy-free"] is False
    assert result["preferences"]["peanut-free"] is False


def test_add_fav_meal(db_session):
    # Add user
    database.add_user("favuser", db_session)

    # Add favorite meal
    database.add_fav_meal("favuser", "Chicken Parmesan")

    # Verify
    user_info = database.get_user_info("favuser")
    assert "Chicken Parmesan" in user_info["fav_meals"]


def test_add_duplicate_fav_meal(db_session):
    # Add user
    database.add_user("dupuser", db_session)

    # Add favorite meal twice
    database.add_fav_meal("dupuser", "Pasta Carbonara")
    database.add_fav_meal("dupuser", "Pasta Carbonara")

    # Verify it appears only once
    user_info = database.get_user_info("dupuser")
    assert user_info["fav_meals"].count("Pasta Carbonara") == 1


def test_remove_fav_meal(db_session):
    # Add user with favorite meal
    database.add_user("remuser", db_session)
    database.add_fav_meal("remuser", "Caesar Salad")

    # Remove favorite meal
    database.remove_fav_meal("remuser", "Caesar Salad")

    # Verify
    user_info = database.get_user_info("remuser")
    assert "Caesar Salad" not in user_info["fav_meals"]
