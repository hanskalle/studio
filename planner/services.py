import json

import requests


class Services:
    def __init__(self, environment, credentials):
        self.environment = environment
        self.credentials = credentials
        self.state_value = {'no': '0', 'yes': '1', 'maybe': '.5'}

    @staticmethod
    def get_uid(self):
        import random
        import string
        return ''.join(random.choice(string.digits + "ABCDEF") for _ in range(32))

    def get_persons_raw(self):
        url = "%s/persons" % self.environment
        return self.get_json(url)

    def get_persons(self):
        persons = {}
        for person in self.get_persons_raw():
            persons[person['name']] = {
                'uid': person['uid'],
                'id': person['id'],
                'email': person['email'],
                'done': person['done'],
            }
        return persons

    def get_missing_persons(self):
        url = "%s/missing-persons" % self.environment
        return self.get_json(url)

    def get_persons_matching(self, name):
        url = "%s/persons/matching/%s" % (self.environment, name)
        return self.get_json(url)

    def get_commitments_raw(self):
        url = "%s/commitments" % self.environment
        return self.get_json(url)

    def get_commitments(self):
        commitments = {}
        for commitment in self.get_commitments_raw():
            task = commitment['task'].replace('_', ' ')
            person = commitment['person'].replace('_', ' ')
            frequency = commitment['frequency']
            if task not in commitments:
                commitments[task] = {}
            commitments[task][person] = frequency
        return commitments

    def get_availabilities_raw(self):
        url = "%s/availabilities" % self.environment
        return self.get_json(url)

    def get_availabilities(self):
        availabilities = {}
        for availability in self.get_availabilities_raw():
            task = availability['task'].replace('_', ' ')
            person = availability['name'].replace('_', ' ')
            week = availability['week']
            available = self.state_value[availability['state']]
            if task not in availabilities:
                availabilities[task] = {}
            if person not in availabilities[task]:
                availabilities[task][person] = {}
            availabilities[task][person][week] = available
        return availabilities

    def post_availability(self, uid, name, task, week, state):
        data = {'uid': uid, 'name': name, 'task': task, 'week': week, 'state': state}
        r = requests.post(self.environment + '/availabilities', data, auth=self.credentials)
        assert r.status_code == 200
        return r.text

    def get_assignments(self):
        url = "%s/assignments" % self.environment
        return self.get_json(url)

    def get_events(self):
        url = "%s/events" % self.environment
        return self.get_json(url)

    def get_json(self, url):
        response = requests.get(url, auth=self.credentials)
        assert response.status_code == 200
        return json.loads(response.text)

    def post_person(self, name, id, email):
        url = "%s/persons" % self.environment
        data = json.dumps({
            "name": name,
            "id": id,
            "done": "0",
            "email": email})
        r = requests.post(url, data, auth=self.credentials)
        assert (r.status_code == 200)
        return r.json()
