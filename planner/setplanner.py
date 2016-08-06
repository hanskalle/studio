#!/usr/bin/env python
import string

domain = 'http://www.ichthusculemborg.nl/services'


def get_uid(size=32, chars=string.digits + "ABCDEF"):
    import random
    return ''.join(random.choice(chars) for _ in range(size))


def post_availability(uid, name, task, week, state):
    import requests
    data = {'uid': uid, 'name': name, 'task': task, 'week': week, 'state': state}
    print(data)
    r = requests.post(domain + '/availabilities', data, auth=('hans.kalle@telfort.nl', password))
    assert r.status_code == 200
    result = r.text
    return result


def exists(availabilities, person, task, week):
    if person in availabilities.keys():
        if task in availabilities[person].keys():
            return week in availabilities[person][task]
    return False


def get_persons(password):
    import requests
    import json
    r = requests.get(domain + "/persons", auth=('hans.kalle@telfort.nl', password))
    assert r.status_code == 200
    persons = {}
    for person in json.loads(r.text):
        persons[person['name']] = {
            'uid': person['uid'],
            'id': person['uid'],
            'email': person['uid'],
            'done': person['uid'],
        }
    return persons


def get_availabilities(password):
    import requests
    import json
    r = requests.get(domain + "/availabilities", auth=('hans.kalle@telfort.nl', password))
    assert r.status_code == 200
    availabilities = {}
    for availability in json.loads(r.text):
        if not availability['name'] in availabilities:
            availabilities[availability['name']] = {}
        person = availabilities[availability['name']]
        if not availability['task'] in person:
            person[availability['task']] = {}
        task = person[availability['task']]
        if not availability['week'] in task:
            task[availability['week']] = availability['state']
    return availabilities


def get_commitments(password):
    import requests
    import json
    r = requests.get(domain + "/commitments", auth=('hans.kalle@telfort.nl', password))
    assert r.status_code == 200
    commitments = {}
    for commitment in json.loads(r.text):
        if not commitment['person'] in commitments:
            commitments[commitment['person']] = {}
        person = commitments[commitment['person']]
        if not commitment['task'] in person:
            person[commitment['task']] = {
                'frequency': commitment['frequency'],
                'remark': commitment['remark']
            }
    return commitments


def show_help():
    print(sys.argv[0], ' [-h] [-f <from week>] [-t <till week>]')
    print('\t-f\tFrom week.')
    print('\t-h\tThis help.')
    print('\t-t\tTill week.')


if __name__ == "__main__":
    import sys
    import getopt
    import getpass

    from_week = 40
    till_week = 52
    domain = "http://www.ichthusculemborg.nl/services"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:t:")
    except getopt.GetoptError:
        print("Incorrect arguments.")
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-f":
            from_week = int(arg)
        elif opt == '-h':
            show_help()
            sys.exit()
        elif opt == "-t":
            till_week = int(arg)
    if from_week > till_week:
        print("Till-week must be greater then from-week.")
        sys.exit(2)
    print('get password')
    password = getpass.getpass('Password for hans.kalle@telfort.nl: ')
    print('get persons')
    persons = get_persons(password)
    print(persons)
    print('get commitments')
    commitments = get_commitments(password)
    print(commitments)
    print('get availability')
    availabilities = get_availabilities(password)
    print(availabilities)
    for person in commitments:
        for task in commitments[person]:
            if person not in ["In_de_dienst", "Niemand"]:
                for week in range(from_week, till_week + 1):
                    if not exists(availabilities, person, task, week):
                        print(post_availability(persons[person]['uid'], person, task, week, "yes"))
