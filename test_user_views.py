"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_2 = User.signup(username="testuser_2",
                            email="test2@test.com",
                            password="testuser2",
                            image_url=None)

        db.session.commit()

        self.testuser_id = self.testuser.id
        self.testuser_2_id = self.testuser_2.id

    def tearDown(self):
        db.session.rollback()

    def test_get_follower_page_logged_in(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            user1 = User.query.get(self.testuser_id)
            user2 = User.query.get(self.testuser_2_id)

            user1.following.append(user2)
            user2.following.append(user1)

            resp = c.get(f"/users/{user2.id}/following")
            resp2 = c.get(f"/users/{user2.id}/followers")

            # Make sure we can see the other user's following and followers pages.
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp2.status_code, 200)

            # Make sure that user 1 is on user2's following page
            # and make sure that user 1 is on user2's followed by page.
            self.assertIn(f"{user1.username}", str(resp.data))
            self.assertIn(f"{user1.username}", str(resp2.data))

    def test_get_follower_page_logged_out(self):
        """Can we see a user's followers or following page when not logged in?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            user1 = User.query.get(self.testuser_id)
            user2 = User.query.get(self.testuser_2_id)

            user1.following.append(user2)
            user2.following.append(user1)

            resp = c.get(f"/users/{user2.id}/following")
            resp2 = c.get(f"/users/{user2.id}/followers")

            # Make sure we cannot see a user's following or followers pages.
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp2.status_code, 302)


