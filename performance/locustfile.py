import json

from locust import HttpUser, task, between, events

class MyUser(HttpUser):
    # Wait time between requests (in seconds)
    wait_time = between(1, 3)

    @task
    def test_get_request(self):
        path = "Cricket/internal/GetSessionSlotDetails.php?series_id=dummy_series&match_id=dummy_match&session=b1&amount=102&room=1"
        # Send a GET request to the endpoint
        with self.client.get(path, catch_response=True) as response:
            if response.status_code == 200:
                # Perform additional checks on the response data
                if 'error' in json.loads(response.text):
                    response.failure("Data does not match expected value")
            else:
                response.failure("Invalid status code")
            self.client.close()
        self.client.close()