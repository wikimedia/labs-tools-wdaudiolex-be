import unittest

from tests.helpers import DbTestCase, make_jwt, make_user


class TestUserRoutes(DbTestCase, unittest.TestCase):
    def test_get_user_requires_auth(self):
        user = make_user()
        response = self.client.get(f"/api/users/{user.id}")
        self.assertEqual(response.status_code, 401)

    def test_get_and_patch_self(self):
        user = make_user()
        token = make_jwt(user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(f"/api/users/{user.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["username"], "Ada")

        patched = self.client.patch(
            f"/api/users/{user.id}",
            headers=headers,
            json={"pref_langs": "en,ibo"},
        )
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.get_json()["pref_langs"], "en,ibo")

    def test_cannot_patch_another_user(self):
        ada = make_user()
        other = make_user("Chidi", temp_token="temp-chidi")
        token = make_jwt(ada)
        response = self.client.patch(
            f"/api/users/{other.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"pref_langs": "fr"},
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
