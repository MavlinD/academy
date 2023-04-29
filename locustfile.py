from locust import HttpUser, SequentialTaskSet, between, task

from src.auth.config import config


class User(HttpUser):
    @task
    class SequenceOfTasks(SequentialTaskSet):
        wait_time = between(1, 5)

        user_credential = {
            "username": config.LOCUST_USERNAME,
            "password": config.LOCUST_PASSWORD,
        }

        @task
        def login(self):
            self.client.post("/api/v2/auth/token-obtain", data=self.user_credential)
