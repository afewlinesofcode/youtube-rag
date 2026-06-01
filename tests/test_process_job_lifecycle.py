import unittest
from unittest.mock import patch

from celery.exceptions import Retry

from app import tasks


class ProcessJobLifecycleTest(unittest.TestCase):
    def test_task_records_retryable_failure_and_schedules_retry(self) -> None:
        queued_job = {"id": "job-id", "status": "queued"}
        running_job = {"id": "job-id", "status": "running", "attempt_count": 1, "max_attempts": 3}
        error = RuntimeError("temporary outage")

        with (
            patch.object(tasks.db, "init_pool"),
            patch.object(tasks, "get_process_job", side_effect=[queued_job, running_job]),
            patch.object(tasks, "run_process_video_job", side_effect=error),
            patch.object(tasks, "mark_process_job_retryable_failure") as mark_retryable,
            patch.object(tasks, "mark_process_job_failed") as mark_failed,
            patch.object(tasks.process_video_job, "retry", side_effect=Retry("retry")) as retry,
        ):
            with self.assertRaises(Retry):
                tasks.process_video_job.run("job-id")

        mark_retryable.assert_called_once_with("job-id", "temporary outage")
        mark_failed.assert_not_called()
        retry.assert_called_once()
        self.assertEqual(retry.call_args.kwargs["countdown"], 10)

    def test_task_records_permanent_failure_without_retry(self) -> None:
        queued_job = {"id": "job-id", "status": "queued"}
        running_job = {"id": "job-id", "status": "running", "attempt_count": 1, "max_attempts": 3}
        error = ValueError("Unsupported YouTube URL")

        with (
            patch.object(tasks.db, "init_pool"),
            patch.object(tasks, "get_process_job", side_effect=[queued_job, running_job]),
            patch.object(tasks, "run_process_video_job", side_effect=error),
            patch.object(tasks, "mark_process_job_retryable_failure") as mark_retryable,
            patch.object(tasks, "mark_process_job_failed") as mark_failed,
            patch.object(tasks.process_video_job, "retry") as retry,
        ):
            with self.assertRaises(ValueError):
                tasks.process_video_job.run("job-id")

        mark_failed.assert_called_once_with(
            "job-id",
            "Unsupported YouTube URL",
            failure_reason="permanent_error",
        )
        mark_retryable.assert_not_called()
        retry.assert_not_called()


if __name__ == "__main__":
    unittest.main()
