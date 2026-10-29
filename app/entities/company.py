from app.extensions import db

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(254), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    owner = db.relationship("User", backref=db.backref("company", uselist=False))
