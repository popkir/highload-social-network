from locust import HttpUser, task, LoadTestShape, TaskSet
import pandas as pd
import requests, json

import locust.stats
locust.stats.CSV_STATS_INTERVAL_SEC = 1
locust.stats.CONSOLE_STATS_INTERVAL_SEC = 10

print("Loading data...")
print('Loading user profiles... from file on disk')
user_profiles_df = pd.read_parquet("../../../app/db/migrations/alembic/mock_data/user_profiles.parquet")
user_names_df = user_profiles_df[["first_name", "last_name"]].drop_duplicates()
print('Loading user ids... via API request')
user_ids_str = requests.get("http://localhost:8085/user/get-ids?number=100000&random=true").content
user_ids_list = json.loads(user_ids_str)
user_ids_df = pd.DataFrame(user_ids_list)
print('Done loading data. Starting load test...')


counter = 0
class UserSearchGetUser(HttpUser):
    @task
    def user_search(self):
        name = user_names_df.sample().iloc[0]
        first_name = name["first_name"]
        last_name = name["last_name"]
        self.client.get("/user/search?first_name={}&last_name={}".format(first_name, last_name))

    @task
    def user_get(self):
        id = user_ids_df.sample().iloc[0][0]
        self.client.get("/user/get/{}".format(id))

    # @task
    # def user_register(self):
    #     global counter
    #     counter += 1

    #     first_name = f'First name {counter}'
    #     last_name = f'Last name {counter}'
    #     bio = f'Bio {counter}'
    #     city = f'City {counter}'
    #     password = f'Password {counter}'
    #     birthday = f'2020-01-01'

    #     payload = {
    #         "first_name": first_name,
    #         "last_name": last_name,
    #         "biography": bio,
    #         "city": city,
    #         "password": password,
    #         "birthday": birthday
    #     }
    #     self.client.post("/user/register", json=payload)


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
        {"duration": 180, "users": 1, "spawn_rate": 1},
        {"duration": 360, "users": 10, "spawn_rate": 10},
        {"duration": 540, "users": 100, "spawn_rate": 100},
        {"duration": 720, "users": 1000, "spawn_rate": 1000}
    ]


    stop_at_end = True

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None