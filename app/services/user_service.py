
from app.repositories import user_repository

def get_user_contributions(user_id):
    # Fetch user contributions from the repository
    return user_repository.get_contributions_by_user(user_id)

