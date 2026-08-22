import unittest

from service import app, db
from service.models import ContributionModel, UserModel


class TestModels(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        user = UserModel(username="Ada", pref_langs="en,ibo")
        db.session.add(user)
        db.session.commit()
        stored = UserModel.query.filter_by(username="Ada").first()
        self.assertIsNotNone(stored)
        self.assertEqual(stored.pref_langs, "en,ibo")

    def test_create_contribution(self):
        contribution = ContributionModel(
            wd_item="L123",
            form_id="L123-F1",
            username="Ada",
            lang_code="ibo",
            audio_filename="LL-Q33578 (ibo)-Ada-ulo.wav",
            edit_type="pronunciation_audio",
            data="P443 added",
        )
        db.session.add(contribution)
        db.session.commit()
        stored = ContributionModel.query.filter_by(form_id="L123-F1").first()
        self.assertIsNotNone(stored)
        self.assertEqual(stored.wd_item, "L123")
        self.assertEqual(stored.edit_type, "pronunciation_audio")


if __name__ == "__main__":
    unittest.main()
