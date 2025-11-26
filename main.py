import random
import storage.movie_storage_sql as db
from colorama import Fore, Back, Style, init
from helpers.helpers_utl import normalize
import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY")

init(autoreset=True)


def fetch_movie_from_api(title):
    """Fetch movie data (title/year/rating/poster) from OMDb API."""

    params = {"apikey": API_KEY, "t": title}  # der Key, den du aus der .env holst
    response = requests.get("http://www.omdbapi.com/", params=params)

    if response.status_code != 200:
        raise ConnectionError("OMDb API unreachable")

    data = response.json()

    if data.get("Response") == "False":
        return None

    return {
        "title": data.get("Title"),
        "year": int(data.get("Year")) if data.get("Year") else None,
        "rating": (
            float(data.get("imdbRating")) if data.get("imdbRating") != "N/A" else None
        ),
        "poster": data.get("Poster"),
    }


def generate_website():
    """Generate index.html using template + current movie database."""
    movie_collection = db.list_movies()
    with open("static/index_template.html", "r") as f:

        template = f.read()
    # 3. Movie Grid konstruieren - weil css
    movie_items = ""
    for title, details in movie_collection.items():
        poster = details.get("poster", "")
        year = details["year"]
        rating = details["rating"]

        movie_items += f"""
        <li>
            <img src="{poster}" alt="{title}" />
            <h3>{title}</h3>
            <p>Year: {year}</p>
            <p>Rating: {rating}</p>
        </li>
        """
    html_output = template.replace("__TEMPLATE_TITLE__", "My Movie Collection")
    html_output = html_output.replace("__TEMPLATE_MOVIE_GRID__", movie_items)

    with open("static/index.html", "w") as f:
        f.write(html_output)

    print("Website was generated successfully.")



def does_movie_exists(title):
    """Return actual DB title if match exists, else None.
    Checks if a movie title exists in the current database (case-insensitive & normalized).
    """
    movie_collection = db.list_movies()
    normalized_title = normalize(title)
    for movie in movie_collection:
        if normalize(movie) == normalized_title:
            return movie
    return None


def validate_rating():
    """
    takes input from user converts to float and checks if input type is correct for rating scale
    :return: validated rating
    """
    while True:
        try:
            rating_input = input("Enter rating (1-10): ").replace(",", ".")
            rating = float(rating_input)
            if 1 <= rating <= 10:
                return rating
            else:
                print("Invalid input! Rating must be between 1 and 10.")
        except ValueError:
            print("Invalid input! Please enter a numeric rating.")


def validate_year():
    """
    checks if movie release year between 1900 - 2025
    :return: release_year
    """
    while True:
        try:
            year_input = input("Enter movie's release year:")
            release_year = int(year_input)
            if 1900 <= release_year <= 2025:
                return release_year
            else:
                print("Invalid input! Rating must be between 1900 and 2025")
        except (ValueError, TypeError) as e:
            print(f"invalid input! Please enter a valid year")


def display_menu():
    """Displays user menu with options"""
    print(
        Style.BRIGHT + Fore.CYAN + Back.BLACK + "*" * 10,
        Style.BRIGHT + Fore.CYAN + Back.BLACK + "My Movie Collection",
        Style.BRIGHT + Fore.CYAN + Back.BLACK + "*" * 10,
        "\n",
    )
    menu = {
        0: "Exit Menu",
        1: "List movies",
        2: "Add movie",
        3: "Delete ",
        4: "Update movie",
        5: "Stats",
        6: "Random movie",
        7: "Search movie",
        8: "Movies sorted by rating",
        9: "Movies sorted by year",
        10: " Generate Website",
    }
    for key, value in menu.items():
        print(Fore.CYAN + f"{key}: {value}")

    print(Back.BLACK + Style.BRIGHT + Fore.CYAN + "*" * 40)


def user_menu_selection():
    """Main menu loop + command routing."""
    keep_commanding = True
    while keep_commanding:
        display_menu()
        choice_made = ""
        try:
            choice_made = input("Enter choice: type 0 - 10 (0 0 to quit): ").strip()
            if choice_made == "0":
                print("Bye...")
                keep_commanding = False
            elif choice_made == "1":
                print("Listing movies...")
                print("")
                list_movies()
            elif choice_made == "2":
                print("Adding movie...")
                add_title()
            elif choice_made == "3":
                print("Deleting movie...")
                delete_title_from_list()
            elif choice_made == "4":
                update_movie_list()
            elif choice_made == "5":
                print("Showing stats...")
                show_stats()
            elif choice_made == "6":
                print("Selecting random movie...")
                show_random_movie()
            elif choice_made == "7":
                print("Searching for movie...")
                search_mov_in_list()
            elif choice_made == "8":
                print("Sorting movies by rating...")
                sort_movies_by_rating()
            elif choice_made == "9":
                print("Sorting movies by year...")
                sort_movie_by_year()
            elif choice_made == "10":
                print("generating website....")
                generate_website()
            else:
                print(
                    "Invalid input. Please try again."
                    "\nChoose a number between 1 and 10 or 0 to quit."
                )
        except KeyboardInterrupt:
            print("\n Bye!")
        input("\nPress Enter to continue...")


def list_movies():
    """Displays all movies in the database with their details"""
    try:
        movie_collection = db.list_movies()
        total_of_movies_in_list = len(movie_collection)
        print(f"{total_of_movies_in_list} movies in total")
        for movie, details in movie_collection.items():
            print(f"{movie} ({details['year']}): {details['rating']}")
    except Exception as e:
        print(f"{e}: error while listing movies.")


def add_title():
    """
    Function to add a movie using the OMDb API.
    :return: None
    """
    try:
        new_title = input("Please enter title: ").strip()
        movie_data = fetch_movie_from_api(new_title)

        if movie_data is None:
            print("Movie not found in OMDb API.")
            return

        # Überprüfen, ob alle benötigten Felder vorhanden sind
        if not all(key in movie_data for key in ("title", "year", "rating", "poster")):
            print("Incomplete data received from API.")
            return

        # Daten aus der API holen
        title = movie_data["title"]
        year = movie_data["year"]
        rating = movie_data["rating"]
        poster = movie_data["poster"]

        # In die Datenbank einfügen
        db.add_movie(title, year, rating, poster)
        print(f"{title} ({year}) added with rating {rating} and poster URL saved.")

    except ConnectionError:
        print("OMDb API not reachable.")
    except ValueError:
        print("Invalid input")


def delete_title_from_list():
    """
    function deletes choice of user
    and saves change to db
    """
    try:
        movie_collection = db.list_movies()
        title_to_delete = input(
            "What title would you like to delete?"
        ).strip()  # .lower().replace("'"," ")
        matched_title = does_movie_exists(title_to_delete)

        if matched_title:
            db.delete_movie(matched_title)
            print(f"{matched_title} has been deleted!")
        else:
            print("Title not in list")
            print("\nAvailable titles:")
            for title in movie_collection:
                print(f"- {title}")
    except ValueError:
        print("Invalid input. Try again!")


def update_movie_list():
    """
    Updates rating of a movie to the db.
    """
    try:
        movie_collection = db.list_movies()
        if not movie_collection:
            print("No movies to update")
            return

        movie_to_update = input("Type in the title to change rating: ").strip()
        matched_title = does_movie_exists(movie_to_update)

        if matched_title:
            rating_to_update = validate_rating()

            # WICHTIG: matched_title NICHT normalisieren
            db.update_movie(matched_title, rating_to_update)

            print(
                f"{matched_title} was successfully updated with rating {rating_to_update}!"
            )
        else:
            print(
                f"'{movie_to_update}' doesn't exist in the list. You can add it via the menu!"
            )

    except Exception as e:
        print(f"Error updating movie: {e}")


def calculate_average():
    """
    function to calculate the average rating of movie database
    :return: average = sum(ratings) / len(ratings)
    """
    try:
        movie_collection = db.list_movies()
        ratings = [movie["rating"] for movie in movie_collection.values()]
        return sum(ratings) / len(ratings)
    except ZeroDivisionError as e:
        print("can't divide through zero")


def show_stats():
    """shows movie w highest / lowest rating / average / median of list"""
    try:
        movie_collection = db.list_movies()
        if not movie_collection:
            print("No movies in collection to show stats.")
            return

        ratings = [movie["rating"] for movie in movie_collection.values()]
        ratings_sorted = sorted(ratings)
        middle = len(ratings_sorted) // 2

        max_rating = max(ratings)
        min_rating = min(ratings)

        best_movies = [
            title
            for title, details in movie_collection.items()
            if details["rating"] == max_rating
        ]
        worst_movies = [
            title
            for title, details in movie_collection.items()
            if details["rating"] == min_rating
        ]

        average_rating = float(calculate_average())

        if len(ratings_sorted) % 2 != 0:
            median_rating = ratings_sorted[middle]
        else:
            median_rating = (ratings_sorted[middle - 1] + ratings_sorted[middle]) / 2

            print(f"Highest rated movie(s) ({max_rating}): {', '.join(best_movies)}")
            print(f"Lowest rated movie(s) ({min_rating}): {', '.join(worst_movies)}")
            print(f"Average rating: {average_rating:.1f}")
            print(f"Median rating: {median_rating:.1f}")

    except (ValueError, TypeError) as e:
        print(f"Error showing stats: {e}")


def show_random_movie():
    """displays a random movie of the list"""
    movie_collection = db.list_movies()
    random_movie, details = random.choice(list(movie_collection.items()))
    print(
        f"Your movie for tonight {random_movie} ({details['year']}). It's rated: {details['rating']} \nEnjoy! "
    )


def search_mov_in_list():
    """search input movie fom user in list"""
    try:
        movie_collection = db.list_movies()
        desired_movie = input("What are you looking for?").strip()

        matched_title = does_movie_exists(desired_movie)

        if matched_title:
            details = movie_collection[matched_title]
            print(
                f"Found movie: {matched_title} - Year: {details['year']} - Rating: {details['rating']}"
            )
        else:
            print("Movie is not in List..")
            new_movie = input("Would you like to add the movie? (Yes or No)").lower()
            if new_movie == "yes":
                add_title()
    except ValueError:
        print("Invalid input! Try again")
    except KeyboardInterrupt:
        print("Invalid input! Try again")


def sort_movies_by_rating():
    """Sort movies by rating (high→low)."""
    movie_collection = db.list_movies()
    sorted_movie_collection = sorted(
        movie_collection.items(), key=lambda details: details[1]["rating"], reverse=True
    )
    for movie, details in sorted_movie_collection:
        print(f"{movie} ({details['year']}): {details['rating']}")


def sort_movie_by_year():
    """Sort movies by year (old→new)."""
    movie_collection = db.list_movies()
    sorted_movie_collection = sorted(
        movie_collection.items(), key=lambda details: details[1]["year"], reverse=False
    )
    for movie, details in sorted_movie_collection:
        print(f"{movie} ({details['year']}): {details['rating']}")


def main():
    """
    Application entry point.
    Starts the interactive menu loop.
    """
    user_menu_selection()


if __name__ == "__main__":
    main()
