from flask_login import UserMixin

from houseminder.db import get_db

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        db = get_db()
        mongo_user = db.houseminder.users.find_one({"id": user_id})
        if not mongo_user:
            return None

        user = User(
            id_=mongo_user['id'],
            name=mongo_user['name'],
            email=mongo_user['email'],
            profile_pic=mongo_user['profile_pic']
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        user = {"id": id_,
                "name": name,
                "email": email,
                "profile_pic": profile_pic}
        db.houseminder.users.insert_one(user)
    