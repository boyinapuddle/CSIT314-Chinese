from datetime import datetime, timezone
from app.extensions import db

class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(16), nullable=False)  # current or past
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    company = db.relationship("Company", backref="projects")
    __table_args__ = (db.CheckConstraint("status IN ('current', 'past')", name="valid_project_status"),)
