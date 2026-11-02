"""Deterministic large-volume test data generator for system testing evidence."""

import random
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from app.database import get_db


SEED = 2026
random.seed(SEED)

app = create_app()

with app.app_context():
    db = get_db()

    profiles = {
        row["name"]: row["profile_id"]
        for row in db.execute("SELECT * FROM user_profiles")
    }
    categories = [
        row["category_id"]
        for row in db.execute(
            "SELECT category_id FROM idp_categories WHERE status = 'Active'"
        )
    ]

    if not profiles or not categories:
        raise SystemExit("Run python seed.py first.")

    for index in range(100):
        username = f"designer{index:03d}"
        db.execute(
            """
            INSERT OR IGNORE INTO user_accounts(
                username,
                password_hash,
                profile_id,
                display_name,
                email
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                generate_password_hash("Test123!"),
                profiles["Interior Designer"],
                f"Designer {index}",
                f"{username}@test.local",
            ),
        )
        row = db.execute(
            "SELECT account_id FROM user_accounts WHERE username = ?",
            (username,),
        ).fetchone()
        designer_id = row[0]
        db.execute(
            """
            INSERT OR IGNORE INTO companies(designer_id, name, description)
            VALUES (?, ?, ?)
            """,
            (
                designer_id,
                f"Studio {index:03d}",
                "Generated scale-test company",
            ),
        )

    for index in range(500):
        username = f"customer{index:04d}"
        db.execute(
            """
            INSERT OR IGNORE INTO user_accounts(
                username,
                password_hash,
                profile_id,
                display_name,
                email
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                generate_password_hash("Test123!"),
                profiles["Customer"],
                f"Customer {index}",
                f"{username}@test.local",
            ),
        )

    designers = [
        row[0]
        for row in db.execute(
            """
            SELECT a.account_id
            FROM user_accounts a
            JOIN user_profiles p ON p.profile_id = a.profile_id
            WHERE p.name = 'Interior Designer'
            """
        )
    ]
    customers = [
        row[0]
        for row in db.execute(
            """
            SELECT a.account_id
            FROM user_accounts a
            JOIN user_profiles p ON p.profile_id = a.profile_id
            WHERE p.name = 'Customer'
            """
        )
    ]

    existing_projects = db.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    for index in range(existing_projects, 2000):
        status = "Past" if index % 3 == 0 else "Current"
        progress = 100 if status == "Past" else random.randint(5, 95)
        updated_at = (
            datetime.utcnow() - timedelta(days=random.randint(0, 180))
        ).isoformat()

        db.execute(
            """
            INSERT INTO projects(
                designer_id,
                category_id,
                title,
                description,
                project_status,
                progress,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                random.choice(designers),
                random.choice(categories),
                f"Scale Project {index:04d}",
                f"Generated project description {index}",
                status,
                progress,
                updated_at,
            ),
        )

    projects = [
        row[0]
        for row in db.execute("SELECT project_id FROM projects")
    ]

    for _ in range(25000):
        viewed_at = (
            datetime.utcnow() - timedelta(days=random.randint(0, 90))
        ).isoformat()
        db.execute(
            """
            INSERT INTO project_views(project_id, customer_id, viewed_at)
            VALUES (?, ?, ?)
            """,
            (
                random.choice(projects),
                random.choice(customers),
                viewed_at,
            ),
        )

    for _ in range(5000):
        saved_at = (
            datetime.utcnow() - timedelta(days=random.randint(0, 90))
        ).isoformat()
        db.execute(
            """
            INSERT OR IGNORE INTO favourites(customer_id, project_id, saved_at)
            VALUES (?, ?, ?)
            """,
            (
                random.choice(customers),
                random.choice(projects),
                saved_at,
            ),
        )

    db.commit()
    print("Large deterministic test dataset generated.")
