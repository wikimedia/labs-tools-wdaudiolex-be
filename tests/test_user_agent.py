import unittest

from service.resources.utils import get_user_agent


class TestUserAgent(unittest.TestCase):
    def test_user_agent_identifies_tool(self):
        header = get_user_agent()
        self.assertIn("User-Agent", header)
        self.assertIn("WDAudioLex/", header["User-Agent"])


if __name__ == "__main__":
    unittest.main()
