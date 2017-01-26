import logging
import requests
import json

class Services:
    def __init__(self, environment, credentials):
        self.environment = environment
        self.credentials = credentials

    def get_commitments(self):
        url = "%s/commitments" % self.environment
        return self.get_json(url)

    def get_availabilities(self):
        url = "%s/availabilities" % self.environment
        return self.get_json(url)

    def get_assignments(self):
        url = "%s/assignments" % self.environment
        return self.get_json(url)

    def get_json(self, url):
        response = requests.get(url, auth = self.credentials)
        assert response.status_code == 200
        return json.loads(response.text)