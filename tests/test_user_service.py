
import unittest
from app.services import user_service

class TestUserService(unittest.TestCase):
    def test_get_user_contributions(self):
        result = user_service.get_user_contributions(1)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()

