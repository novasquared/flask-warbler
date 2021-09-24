"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
from flask_bcrypt import Bcrypt


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

bcrypt = Bcrypt()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        Likes.query.delete()
        Message.query.delete()
        Follows.query.delete()
        User.query.delete()

        self.client = app.test_client()

        test_u1 = User(email="testemail1@test.com",
                        username="testuser1",
                        password="hashedpass1")

        test_u2 = User(email="testemail2@test.com",
                        username="testuser2",
                        password="hashedpass2")

        test_u3 = User(email="testemail3@test.com",
                        username="testuser3",
                        password="hashedpass3")


        db.session.add(test_u1)
        db.session.add(test_u2)
        db.session.add(test_u3)

        db.session.commit()

        self.test_u1_id = test_u1.id
        self.test_u2_id = test_u2.id
        self.test_u3_id = test_u3.id
    
    def tearDown(self):
        """Stuff to do after every test."""
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """does the repr method work?"""

        test_user = User.query.get(self.test_u1_id)
        
        self.assertEqual(test_user.__repr__(), f"<User #{test_user.id}: {test_user.username}, {test_user.email}>")


    def test_user_signup(self):
        """Does signup return the correct user"""

        test_user_sign_up = User.signup("Jeanne", "test@test.com", "testing123", None)

        db.session.commit()

        self.assertEqual(test_user_sign_up.username, "Jeanne")
        self.assertEqual(test_user_sign_up.email, "test@test.com")

        self.assertTrue(bcrypt.check_password_hash(test_user_sign_up.password, "testing123"))

    def test_successful_follow(self):
        """does is following detect succeesful follow
        does is following know when somebody is not following
        does is followed by detect both successful followed by and not followed by"""

        user_1 = User.query.get(self.test_u1_id)
        user_2 = User.query.get(self.test_u2_id)

        user_1.following.append(user_2)

        db.session.commit()

        # tests if user_1 is following user_2 and if user_2 is followed by user_1
        self.assertTrue(user_1.is_following(user_2))
        self.assertTrue(user_2.is_followed_by(user_1))

        # tests to make sure that user_2 is not following user_1 and user_2 is not following user_1
        # since we set it up that way
        self.assertFalse(user_2.is_following(user_1))
        self.assertFalse(user_1.is_followed_by(user_2))



    
    #does user.signup detect correct user, and does it error on incorrect credentials
    #does user.authenticate find correct user or fail to authenticate when user not found based on email / password