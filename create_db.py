from service import app, db
from service.models import ContributionModel, UserModel  # noqa: F401

with app.app_context():
    db.create_all()
    print("Database tables created.")
