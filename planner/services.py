import json

import requests


class Services:
    def __init__(self, host, login, services, credentials):
        self.environment = host + services
        self.session = requests.Session()
        self.session.get(host + login)
        self.session.post(host + login, {
            'log': credentials[0],
            'pwd': credentials[1],
            'rememberme': 'forever',
            'redirect_to': host + services,
            'testcookie': 1,
            'wp-submit': 'Log%20In'
        })
        self.state_value = {'no': '0', 'yes': '1', 'maybe': '.5'}

    @staticmethod
    def get_uid():
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
        print(name)
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
        url = "%s/availabilities" % self.environment
        data = json.dumps({
            'uid': uid,
            'name': name,
            'task': task,
            'week': week,
            'state': state
        })
        r = self.session.post(url, data)
        if r.status_code != 200:
            print(r.status_code, data)
        assert (r.status_code == 200)
        return r.text

    def get_assignments(self):
        url = "%s/assignments" % self.environment
        return self.get_json(url)

    def get_events(self):
        url = "%s/events" % self.environment
        return self.get_json(url)

    def get_json(self, url):
        response = self.session.get(url)
        assert response.status_code == 200
        return json.loads(response.text)

    def post_person(self, name, user_id, email):
        url = "%s/persons" % self.environment
        data = json.dumps({
            "name": name,
            "id": user_id,
            "done": "0",
            "email": email})
        r = self.session.post(url, data)
        assert (r.status_code == 200)
        return r.json()

    def create_event(self, eventdate, eventtime, description, location, remark):
        from datetime import datetime

        def create_start(the_date, the_time):
            return datetime.combine(the_date, the_time).isoformat()

        url = "%s/events" % self.environment
        data = json.dumps({
            "start": create_start(eventdate, eventtime),
            "description": description,
            "location": location,
            "remark": remark})
        print(data)
        r = self.session.post(url, data)
        assert (r.status_code == 200)
        return r.json()

    def create_assignment(self, event_uid, task, person, remark):
        url = "%s/events/%s/assignments" % (self.environment, event_uid)
        data = json.dumps({
            "task": task,
            "person": person,
            "remark": remark})
        print(data)
        r = self.session.post(url, data)
        assert (r.status_code == 200)
        return r.json()

    def delete_assignment(self, uid):
        url = "%s/assignments/%s" % (self.environment, uid)
        r = self.session.delete(url)
        assert (r.status_code == 200)
        return
