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

    profiles = [
        ("User Admin", "Manage user profiles and accounts", "User Admin"),
        (
            "Interior Designer",
            "Manage company information and Interior Design Projects",
            "Interior Designer",
        ),
        ("Customer", "Explore, view and save Interior Design Projects", "Customer"),
        (
            "Platform Manager",
            "Manage categories and analyse platform performance",
            "Platform Manager",
        ),
    ]
    db.executemany(
        "INSERT INTO user_profiles(name, description, role) VALUES(?,?,?)",
        profiles,
    )
    profile_ids = {
        row["name"]: row["profile_id"]
        for row in db.execute("SELECT * FROM user_profiles")
    }

    account_data = [
        ("admin", "Admin123!", "User Admin", "Avery Admin", "admin@example.com"),
        ("admin2", "Admin123!", "User Admin", "Amelia Admin", "admin2@example.com"),
        (
            "designer",
            "Designer123!",
            "Interior Designer",
            "Dina Designer",
            "designer@example.com",
        ),
        (
            "designer2",
            "Designer123!",
            "Interior Designer",
            "Ethan Designer",
            "designer2@example.com",
        ),
        (
            "designer3",
            "Designer123!",
            "Interior Designer",
            "Farah Designer",
            "designer3@example.com",
        ),
        ("customer", "Customer123!", "Customer", "Casey Customer", "customer@example.com"),
        ("customer2", "Customer123!", "Customer", "Chloe Customer", "customer2@example.com"),
        ("customer3", "Customer123!", "Customer", "Daniel Customer", "customer3@example.com"),
        ("customer4", "Customer123!", "Customer", "Emma Customer", "customer4@example.com"),
        ("customer5", "Customer123!", "Customer", "Felix Customer", "customer5@example.com"),
        ("customer6", "Customer123!", "Customer", "Grace Customer", "customer6@example.com"),
        ("customer7", "Customer123!", "Customer", "Hannah Customer", "customer7@example.com"),
        ("customer8", "Customer123!", "Customer", "Isaac Customer", "customer8@example.com"),
        (
            "manager",
            "Manager123!",
            "Platform Manager",
            "Morgan Manager",
            "manager@example.com",
        ),
        (
            "manager2",
            "Manager123!",
            "Platform Manager",
            "Maya Manager",
            "manager2@example.com",
        ),
    ]

    accounts = [
        (
            username,
            generate_password_hash(password),
            profile_ids[profile_name],
            display_name,
            email,
        )
        for username, password, profile_name, display_name, email in account_data
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

    companies = [
        (
            account_ids["designer"],
            "Northline Studio",
            "Residential interiors focused on warm minimalism, practical planning and natural materials.",
            "+65 6123 4567",
            "hello@northline.example",
            "https://northline.example",
            "Singapore",
        ),
        (
            account_ids["designer2"],
            "Form and Field",
            "Contemporary residential and workplace interiors with a focus on flexible spaces.",
            "+65 6234 5678",
            "studio@formfield.example",
            "https://formfield.example",
            "Singapore",
        ),
        (
            account_ids["designer3"],
            "Still House Design",
            "Calm family homes combining natural textures, custom joinery and thoughtful lighting.",
            "+65 6345 6789",
            "hello@stillhouse.example",
            "https://stillhouse.example",
            "Johor Bahru",
        ),
    ]
    db.executemany(
        "INSERT INTO companies(designer_id, name, description, phone, email, website, address) "
        "VALUES(?,?,?,?,?,?,?)",
        companies,
    )

    categories = [
        ("Modern", "Clean lines, restrained palettes and functional layouts"),
        ("Scandinavian", "Light woods, calm tones and comfortable simplicity"),
        ("Contemporary", "Current materials and refined urban detailing"),
        ("Japandi", "Japanese restraint combined with Scandinavian warmth"),
        ("Industrial", "Raw textures, metal details and practical open planning"),
        ("Minimalist", "Simple forms, uncluttered layouts and carefully selected materials"),
    ]
    db.executemany(
        "INSERT INTO idp_categories(name, description) VALUES(?,?)",
        categories,
    )
    category_ids = {
        row["name"]: row["category_id"]
        for row in db.execute("SELECT * FROM idp_categories")
    }

    now = datetime.now(UTC).replace(tzinfo=None)
    project_data = [
        ("designer", "Modern", "Tiong Bahru Calm", "Compact apartment with hidden storage and warm stone finishes.", "Current", 68, 1),
        ("designer", "Japandi", "Quiet Courtyard Home", "Family home with oak joinery, tactile plaster and framed daylight.", "Current", 42, 3),
        ("designer", "Scandinavian", "Bright Resale Refresh", "Completed resale transformation with pale timber and flexible dining.", "Past", 100, 12),
        ("designer", "Contemporary", "City Lines", "Polished apartment with layered lighting and dark accents.", "Past", 100, 24),
        ("designer", "Minimalist", "Soft Edge Apartment", "A calm apartment planned around concealed storage and curved joinery.", "Current", 55, 6),
        ("designer2", "Industrial", "Workshop Loft", "Open loft with exposed structure, black steel and adaptable work zones.", "Current", 74, 2),
        ("designer2", "Contemporary", "Orchard Office", "Flexible workplace with meeting pods, acoustic finishes and shared social zones.", "Current", 61, 5),
        ("designer2", "Modern", "Harbour View Suite", "Apartment renovation with strong sight lines and integrated lighting.", "Past", 100, 18),
        ("designer2", "Scandinavian", "Family First Home", "Practical family home with durable finishes and generous storage.", "Past", 100, 32),
        ("designer2", "Minimalist", "Compact Studio", "Small studio using sliding partitions and built in furniture.", "Current", 35, 8),
        ("designer3", "Japandi", "Woodland Retreat", "Textural home using timber, limewash and soft indirect lighting.", "Current", 81, 4),
        ("designer3", "Modern", "Lakefront Apartment", "Open plan home with stone surfaces and custom display joinery.", "Current", 48, 7),
        ("designer3", "Minimalist", "Quiet Family House", "Completed family house focused on natural light and uncluttered circulation.", "Past", 100, 16),
        ("designer3", "Industrial", "Creative Studio", "Completed creative workspace with exposed services and modular furniture.", "Past", 100, 27),
        ("designer3", "Contemporary", "Garden Residence", "Layered residence connecting indoor living areas with planted terraces.", "Current", 29, 10),
    ]

    image_urls = [
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
    ]

    projects = []
    for index, (designer, category, title, description, status, progress, days_ago) in enumerate(project_data):
        projects.append(
            (
                account_ids[designer],
                category_ids[category],
                title,
                description,
                status,
                progress,
                image_urls[index % len(image_urls)],
                (now - timedelta(days=days_ago)).isoformat(),
            )
        )
    db.executemany(
        "INSERT INTO projects(designer_id, category_id, title, description, project_status, progress, image_url, updated_at) "
        "VALUES(?,?,?,?,?,?,?,?)",
        projects,
    )

    project_rows = list(db.execute("SELECT project_id, designer_id, title, updated_at FROM projects ORDER BY project_id"))
    customer_names = [f"customer{i}" for i in range(2, 9)] + ["customer"]
    customer_ids = [account_ids[name] for name in customer_names]

    # Historical account creation and login activity gives daily, weekly and monthly reports useful data.
    for index, (username, _password, _profile, _display, _email) in enumerate(account_data):
        account_id = account_ids[username]
        created_at = now - timedelta(days=(index * 3) % 42, hours=index % 8)
        db.execute(
            "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
            ("account_created", account_id, None, created_at.isoformat()),
        )
        for login_index in range(4):
            login_at = now - timedelta(days=(index + login_index * 5) % 28, hours=(index * 2 + login_index) % 12)
            db.execute(
                "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
                ("login_success", account_id, None, login_at.isoformat()),
            )

    # Project creation and update history.
    for index, row in enumerate(project_rows):
        created_at = now - timedelta(days=min(40, 5 + index * 2))
        db.execute(
            "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
            ("project_created", row["designer_id"], row["project_id"], created_at.isoformat()),
        )
        if index % 3 != 0:
            updated_at = now - timedelta(days=index % 9, hours=index % 6)
            db.execute(
                "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
                ("project_updated", row["designer_id"], row["project_id"], updated_at.isoformat()),
            )

    # Project views are spread across the last 35 days and across multiple customers.
    for project_index, row in enumerate(project_rows):
        view_count = 16 + project_index * 3
        for view_index in range(view_count):
            customer_id = customer_ids[(project_index + view_index) % len(customer_ids)]
            viewed_at = now - timedelta(
                days=(project_index * 2 + view_index) % 35,
                hours=(view_index * 3) % 20,
            )
            db.execute(
                "INSERT INTO project_views(project_id, customer_id, viewed_at) VALUES(?,?,?)",
                (row["project_id"], customer_id, viewed_at.isoformat()),
            )
            db.execute(
                "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
                ("project_viewed", customer_id, row["project_id"], viewed_at.isoformat()),
            )

    # Current favourites provide shortlist analytics for several categories and projects.
    favourite_pairs = []
    for customer_index, customer_id in enumerate(customer_ids):
        for project_index, row in enumerate(project_rows):
            if (customer_index + project_index) % 4 == 0:
                saved_at = now - timedelta(
                    days=(customer_index * 3 + project_index) % 27,
                    hours=(customer_index + project_index) % 12,
                )
                favourite_pairs.append((customer_id, row["project_id"], saved_at))

    for customer_id, project_id, saved_at in favourite_pairs:
        db.execute(
            "INSERT INTO favourites(customer_id, project_id, saved_at) VALUES(?,?,?)",
            (customer_id, project_id, saved_at.isoformat()),
        )
        db.execute(
            "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
            ("project_shortlisted", customer_id, project_id, saved_at.isoformat()),
        )

    # Historical removals from favourites are kept as activity events for report analysis.
    for index in range(12):
        customer_id = customer_ids[index % len(customer_ids)]
        project_id = project_rows[(index * 2 + 1) % len(project_rows)]["project_id"]
        removed_at = now - timedelta(days=index % 14, hours=index)
        db.execute(
            "INSERT INTO activity_events(event_type, account_id, project_id, created_at) VALUES(?,?,?,?)",
            ("project_unshortlisted", customer_id, project_id, removed_at.isoformat()),
        )

    db.commit()
    return True
