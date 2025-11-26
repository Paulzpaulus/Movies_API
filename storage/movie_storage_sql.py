from sqlalchemy import create_engine, text

# Database URL
DB_URL = "sqlite:///movies.db"

# Create engine
engine = create_engine(DB_URL)

# Create the movies table with POSTER support
with engine.begin() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT
        )
    """))


def list_movies():
    """
    Retrieve all movies from DB.
    Returns:
        dict: {title: {"year":..., "rating":..., "poster":...}}
    """
    with engine.begin() as connection:
        result = connection.execute(text("""
            SELECT title, year, rating, poster FROM movies
        """))
        rows = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster": row[3]
        }
        for row in rows
    }


def add_movie(title, year, rating, poster):
    """Insert movie into DB."""
    with engine.begin() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster)
                    VALUES (:title, :year, :rating, :poster)
                """),
                {"title": title, "year": year, "rating": rating, "poster": poster}
            )
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error inserting movie: {e}")


def delete_movie(title):
    """Delete movie from DB."""
    with engine.begin() as connection:
        try:
            connection.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title}
            )
        except Exception as e:
            print(f"Error deleting movie: {e}")


def update_movie(title, rating):
    """Update rating in DB."""
    with engine.begin() as connection:
        try:
            connection.execute(
                text("""
                    UPDATE movies
                    SET rating = :rating
                    WHERE title = :title
                """),
                {"rating": rating, "title": title}
            )
        except Exception as e:
            print(f"Error updating movie: {e}")

