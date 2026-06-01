import unittest
from unittest.mock import patch

from app.services import video_service


class VideoServiceTest(unittest.TestCase):
    def test_create_video_process_job_returns_succeeded_job_for_existing_video(self) -> None:
        existing_video = {"id": "video-id"}
        succeeded_job = {"id": "job-id", "status": "succeeded", "video_id": "video-id"}

        with (
            patch.object(video_service, "get_video_by_youtube_video_id", return_value=existing_video),
            patch.object(video_service, "create_succeeded_process_job", return_value=succeeded_job),
        ):
            self.assertEqual(video_service.create_video_process_job("https://youtu.be/youtube-id"), succeeded_job)

    def test_create_video_process_job_returns_active_job_for_same_video(self) -> None:
        active_job = {"id": "job-id", "status": "running", "video_id": None}

        with (
            patch.object(video_service, "get_video_by_youtube_video_id", return_value=None),
            patch.object(video_service, "get_active_process_job_by_youtube_video_id", return_value=active_job),
        ):
            self.assertEqual(video_service.create_video_process_job("https://youtu.be/youtube-id"), active_job)

    def test_create_video_process_job_queues_new_video(self) -> None:
        queued_job = {"id": "job-id", "status": "queued", "video_id": None}

        with (
            patch.object(video_service, "get_video_by_youtube_video_id", return_value=None),
            patch.object(video_service, "get_active_process_job_by_youtube_video_id", return_value=None),
            patch.object(video_service, "create_process_job", return_value=queued_job),
            patch.object(video_service.process_video_job, "delay") as delay,
            patch.object(video_service, "logger"),
        ):
            self.assertEqual(video_service.create_video_process_job("https://youtu.be/youtube-id"), queued_job)

        delay.assert_called_once_with("job-id")


if __name__ == "__main__":
    unittest.main()
