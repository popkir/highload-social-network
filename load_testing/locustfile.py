from locust import HttpUser, task, LoadTestShape
import pandas as pd

import locust.stats
locust.stats.CSV_STATS_INTERVAL_SEC = 1
locust.stats.CONSOLE_STATS_INTERVAL_SEC = 10


# class HealthCheckUser(HttpUser):
#     @task
#     def health_check(self):
#         self.client.get("/health-check")


user_profiles_df = pd.read_parquet("../app/db/migrations/alembic/mock_data/user_profiles.parquet")
user_names_df = user_profiles_df[["first_name", "last_name"]].drop_duplicates()

class UserSearchUser(HttpUser):
    @task
    def user_search(self):
        name = user_names_df.sample().iloc[0]
        first_name = name["first_name"]
        last_name = name["last_name"]
        self.client.get("/user/search?first_name={}&last_name={}".format(first_name, last_name))

class StagesShape(LoadTestShape):
    """
    A simply load test shape class that has different user and spawn_rate at
    different stages.
    Keyword arguments:
        stages -- A list of dicts, each representing a stage with the following keys:
            duration -- When this many seconds pass the test is advanced to the next stage
            users -- Total user count
            spawn_rate -- Number of users to start/stop per second
            stop -- A boolean that can stop that test at a specific stage
        stop_at_end -- Can be set to stop once all stages have run.
    """

    stages = [
        {"duration": 120, "users": 1, "spawn_rate": 1},
        {"duration": 240, "users": 10, "spawn_rate": 10},
        {"duration": 360, "users": 100, "spawn_rate": 100},
        {"duration": 480, "users": 1000, "spawn_rate": 1000}
    ]

    stop_at_end = True

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None