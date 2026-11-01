from app import create_app
from app.database import get_db
from app.seed_data import seed_database


def main():
    app = create_app({"TESTING": True})
    with app.app_context():
        seed_database(get_db(), reset=True)
    print("Seeded demo database.")


if __name__ == "__main__":
    main()
