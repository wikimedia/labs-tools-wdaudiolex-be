import unittest
from unittest.mock import MagicMock, patch

from service.models import ContributionModel
from tests.helpers import DbTestCase, make_jwt, make_user


def _json_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.status_code = 200
    return response


class TestLexemeAudioAdd(DbTestCase, unittest.TestCase):
    def test_requires_auth(self):
        response = self.client.post("/api/lexeme/audio/add", json={
            "formid": "L123-F1",
            "filename": "LL-Q33578 (ibo)-Ada-ulo.wav",
            "lang_wdqid": "Q33578",
        })
        self.assertEqual(response.status_code, 401)

    @patch("service.resources.wikidata.utils.requests.post")
    @patch("service.resources.wikidata.utils.generate_csrf_token")
    def test_writes_claim_then_stores_contribution(self, mock_csrf, mock_post):
        mock_csrf.return_value = ("csrf-token", object())
        mock_post.side_effect = [
            _json_response({
                "success": 1,
                "claim": {"id": "L123$uuid"},
                "pageinfo": {"lastrevid": 10},
            }),
            _json_response({"success": 1, "pageinfo": {"lastrevid": 11}}),
            _json_response({"success": 1, "pageinfo": {"lastrevid": 12}}),
        ]
        user = make_user()
        token = make_jwt(user)
        response = self.client.post(
            "/api/lexeme/audio/add",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "formid": "L123-F1",
                "filename": "File:LL-Q33578 (ibo)-Ada-ulo.wav",
                "lang_wdqid": "Q33578",
                "variety_qid": "Q123",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["lexeme_id"], "L123")
        self.assertEqual(payload["form_id"], "L123-F1")
        self.assertEqual(payload["filename"], "LL-Q33578 (ibo)-Ada-ulo.wav")
        self.assertTrue(payload["contribution_id"])
        stored = ContributionModel.query.first()
        self.assertIsNotNone(stored)
        self.assertEqual(stored.username, "Ada")
        self.assertEqual(stored.edit_type, "pronunciation_audio")
        self.assertEqual(stored.variety_qid, "Q123")
        self.assertEqual(mock_post.call_count, 3)

    @patch("service.resources.wikidata.utils.requests.post")
    @patch("service.resources.wikidata.utils.generate_csrf_token")
    def test_wikidata_error_does_not_store(self, mock_csrf, mock_post):
        mock_csrf.return_value = ("csrf-token", object())
        mock_post.return_value = _json_response({
            "error": {"code": "failed", "info": "nope"}
        })
        user = make_user()
        token = make_jwt(user)
        response = self.client.post(
            "/api/lexeme/audio/add",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "formid": "L123-F1",
                "filename": "ulo.wav",
                "lang_wdqid": "Q33578",
            },
        )
        self.assertEqual(response.status_code, 503)
        self.assertIsNone(ContributionModel.query.first())

    def test_contributions_filter(self):
        user = make_user()
        token = make_jwt(user)
        from service import db
        from datetime import datetime, timezone
        row = ContributionModel(
            wd_item="L123",
            form_id="L123-F1",
            username="Ada",
            lang_code="Q33578",
            audio_filename="ulo.wav",
            edit_type="pronunciation_audio",
            date=datetime.now(timezone.utc),
        )
        db.session.add(row)
        db.session.commit()
        response = self.client.get(
            "/api/contributions?username=Ada",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)


if __name__ == "__main__":
    unittest.main()
