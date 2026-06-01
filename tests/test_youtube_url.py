import unittest

from app.gateways.youtube.url import extract_youtube_video_id


class YouTubeUrlTest(unittest.TestCase):
    def test_extract_youtube_video_id(self) -> None:
        examples = [
            ("https://www.youtube.com/watch?v=abc123&t=20", "abc123"),
            ("https://youtu.be/abc123?si=test", "abc123"),
            ("https://www.youtube.com/shorts/abc123", "abc123"),
            ("https://www.youtube.com/embed/abc123", "abc123"),
        ]

        for url, video_id in examples:
            with self.subTest(url=url):
                self.assertEqual(extract_youtube_video_id(url), video_id)

    def test_extract_youtube_video_id_rejects_unsupported_url(self) -> None:
        with self.assertRaises(ValueError):
            extract_youtube_video_id("https://example.com/watch?v=abc123")


if __name__ == "__main__":
    unittest.main()
