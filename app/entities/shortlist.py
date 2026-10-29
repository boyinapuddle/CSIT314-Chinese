from datetime import datetime, timezone
from app.extensions import db

class Shortlist(db.Model):
    __tablename__ = "shortlists"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    # An anonymous visitor token allows a demonstrable count without adding customer accounts.
    visitor_token = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint("project_id", "visitor_token", name="uq_shortlist_project_visitor"),)
