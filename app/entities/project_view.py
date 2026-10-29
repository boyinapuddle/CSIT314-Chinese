from datetime import datetime, timezone
from app.extensions import db

class ProjectView(db.Model):
    __tablename__ = "project_views"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    viewed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
