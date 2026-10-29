"""Non-destructive demo provisioning, outside the formal story controllers."""
import click
from sqlalchemy.exc import IntegrityError

from app.entities import Company, Project, ProjectView, Shortlist, User
from app.extensions import db


def register_demo_command(app):
    @app.cli.command("seed-demo")
    @click.option("--email", default="demo.designer@example.com", show_default=True)
    @click.password_option()
    def seed_demo(email, password):
        """Add a fresh demo designer and portfolio; never overwrite existing data."""
        email = email.strip().lower()
        if not email or len(email) > 254 or "@" not in email:
            raise click.ClickException("Provide a valid demo email address.")
        if len(password) < 12:
            raise click.ClickException("Password must be at least 12 characters.")
        if db.session.scalar(db.select(User).filter_by(email=email)):
            raise click.ClickException("Email already exists. Choose a new demo email; existing data was not changed.")
        user = User(email=email)
        user.set_password(password)
        company = Company(owner=user, name="Atelier Sample / Demo Studio",
                          description="Demonstration portfolio for a text-first interior design practice.",
                          email="studio@example.com", phone="+65 6000 0000", address="Singapore (demo)")
        db.session.add(company)
        try:
            db.session.flush()
            for title, status, description, views, shortlists in (
                ("Serangoon Courtyard Home", "current", "An ongoing home renovation with warm timber and an open living space.", 5, 2),
                ("River Valley Compact Studio", "current", "An ongoing apartment design with flexible storage and soft neutral finishes.", 2, 1),
                ("Tiong Bahru Reading House", "past", "A completed home with quiet reading corners and restored details.", 8, 3),
                ("East Coast Family Apartment", "past", "A completed family home with durable finishes and a generous dining space.", 0, 0),
            ):
                project = Project(company=company, title=title, status=status,
                                  description="DEMO DATA: " + description)
                db.session.add(project)
                db.session.flush()
                db.session.add_all([ProjectView(project_id=project.id) for _ in range(views)])
                db.session.add_all([Shortlist(project_id=project.id, visitor_token=f"demo-visitor-{i}")
                                    for i in range(shortlists)])
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise click.ClickException("Demo could not be created. No partial demo records were saved.") from None
        click.echo(f"Demo designer created: {email}")
        click.echo("Added one company, two current projects and two past projects.")
        click.echo("The 15 views and 6 shortlists are synthetic demonstration data.")
