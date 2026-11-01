from datetime import UTC, datetime, timedelta

from werkzeug.security import generate_password_hash


def seed_database(db, reset=False):
    if reset:
        for table in [
            "activity_events",
            "project_views",
            "favourites",
            "projects",
            "companies",
            "user_sessions",
            "user_accounts",
            "idp_categories",
            "user_profiles",
        ]:
            db.execute(f"DELETE FROM {table}")
    else:
        existing_accounts = db.execute(
            "SELECT COUNT(*) AS total FROM user_accounts"
        ).fetchone()["total"]
        if existing_accounts:
            return False

    roles = [
        ("User Admin", "Manage user profiles and accounts", "User Admin"),
        ("Interior Designer", "Manage company and project portfolio", "Interior Designer"),
        ("Customer", "Explore and save IDPs", "Customer"),
        ("Platform Manager", "Manage categories and reports", "Platform Manager"),
    ]
    db.executemany(
        "INSERT INTO user_profiles(name, description, role) VALUES(?,?,?)",
        roles,
    )
    profile_ids = {
        row["name"]: row["profile_id"]
        for row in db.execute("SELECT * FROM user_profiles")
    }

    accounts = [
        (
            "admin",
            generate_password_hash("Admin123!"),
            profile_ids["User Admin"],
            "Avery Admin",
            "admin@example.com",
        ),
        (
            "designer",
            generate_password_hash("Designer123!"),
            profile_ids["Interior Designer"],
            "Dina Designer",
            "designer@example.com",
        ),
        (
            "customer",
            generate_password_hash("Customer123!"),
            profile_ids["Customer"],
            "Casey Customer",
            "customer@example.com",
        ),
        (
            "manager",
            generate_password_hash("Manager123!"),
            profile_ids["Platform Manager"],
            "Morgan Manager",
            "manager@example.com",
        ),
    ]
    db.executemany(
        "INSERT INTO user_accounts(username, password_hash, profile_id, display_name, email) "
        "VALUES(?,?,?,?,?)",
        accounts,
    )
    account_ids = {
        row["username"]: row["account_id"]
        for row in db.execute("SELECT * FROM user_accounts")
    }

    db.execute(
        "INSERT INTO companies(designer_id, name, description, phone, email, website, address) "
        "VALUES(?,?,?,?,?,?,?)",
        (
            account_ids["designer"],
            "Northline Studio",
            "Residential interiors focused on warm minimalism, practical planning and natural materials.",
            "+65 6123 4567",
            "hello@northline.example",
            "https://example.com",
            "Singapore",
        ),
    )

    categories = [
        ("Modern", "Clean lines, restrained palettes and functional layouts"),
        ("Scandinavian", "Light woods, calm tones and comfortable simplicity"),
        ("Contemporary", "Current materials and refined urban detailing"),
        ("Japandi", "Japanese restraint combined with Scandinavian warmth"),
    ]
    db.executemany(
        "INSERT INTO idp_categories(name, description) VALUES(?,?)",
        categories,
    )
    category_ids = {
        row["name"]: row["category_id"]
        for row in db.execute("SELECT * FROM idp_categories")
    }

    now = datetime.now(UTC)
    projects = [
        (
            account_ids["designer"], category_ids["Modern"], "Tiong Bahru Calm",
            "A compact apartment reworked around hidden storage, soft stone finishes and an open living core.",
            "Current", 68,
            "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=80",
            (now - timedelta(days=1)).isoformat(),
        ),
        (
            account_ids["designer"], category_ids["Japandi"], "Quiet Courtyard Home",
            "A serene family home balancing oak joinery, tactile plaster and carefully framed daylight.",
            "Current", 42,
            "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
            (now - timedelta(days=2)).isoformat(),
        ),
        (
            account_ids["designer"], category_ids["Scandinavian"], "Bright Resale Refresh",
            "A completed resale transformation with pale timber, flexible dining and generous concealed storage.",
            "Past", 100,
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            (now - timedelta(days=15)).isoformat(),
        ),
        (
            account_ids["designer"], category_ids["Contemporary"], "City Lines",
            "A polished apartment with layered lighting, dark accents and a gallery-like living space.",
            "Past", 100,
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
            (now - timedelta(days=25)).isoformat(),
        ),
    ]
    db.executemany(
        "INSERT INTO projects(designer_id, category_id, title, description, project_status, progress, image_url, updated_at) "
        "VALUES(?,?,?,?,?,?,?,?)",
        projects,
    )

    project_ids = [
        row["project_id"]
        for row in db.execute("SELECT project_id FROM projects")
    ]
    for project_id in project_ids:
        for index in range(project_id * 2):
            db.execute(
                "INSERT INTO project_views(project_id, customer_id, viewed_at) VALUES(?,?,?)",
                (
                    project_id,
                    account_ids["customer"],
                    (now - timedelta(days=index % 5)).isoformat(),
                ),
            )

    db.execute(
        "INSERT INTO favourites(customer_id, project_id, saved_at) VALUES(?,?,?)",
        (account_ids["customer"], project_ids[0], now.isoformat()),
    )
    db.execute(
        "INSERT INTO favourites(customer_id, project_id, saved_at) VALUES(?,?,?)",
        (
            account_ids["customer"],
            project_ids[2],
            (now - timedelta(days=2)).isoformat(),
        ),
    )

    for event_type, project_id in [
        ("project_viewed", project_ids[0]),
        ("project_shortlisted", project_ids[0]),
        ("project_viewed", project_ids[1]),
        ("project_created", project_ids[1]),
    ]:
        db.execute(
            "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
            (event_type, account_ids["customer"], project_id, now.isoformat()),
        )

    db.commit()
    return True
