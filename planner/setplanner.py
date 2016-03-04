#!/usr/bin/env python
import string


def get_uid(size=32, chars=string.digits + "ABCDEF"):
    import random
    return ''.join(random.choice(chars) for _ in range(size))


def post_availability(uid, name, task, week, state):
    print uid, name, task, week, state
    import httplib
    import urllib
    conn = httplib.HTTPConnection("ichthusculemborg.nl")
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "application/json"}
    params = urllib.urlencode({'uid': uid, 'name': name, 'task': task, 'week': week, 'state': state})
    conn.request("POST", "/planner/persons", params, headers)
    response = conn.getresponse()
    assert (response.status == 200)
    result = response.read()
    conn.close()
    return result


def get_persons(password):
    import httplib
    import urllib
    import json
    params = urllib.urlencode({'email': 'hans.kalle@telfort.nl', 'wachtwoord': password})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("www.ichthusculemborg.nl")
    conn.request("POST", "/intranet/login.asp?p=/planner/ready", params, headers)
    response = conn.getresponse()
    if response.status == 302:
        response.read()
        location = response.getheader('location')
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "Cookie": response.getheader('set-cookie')}
        conn.request("GET", location, '', headers)
        response = conn.getresponse()
    else:
        return []
    assert (response.status == 200)
    persons = response.read()
    return json.loads(persons)


def get_availability(password):
    import httplib
    import urllib
    import json
    params = urllib.urlencode({'email': 'hans.kalle@telfort.nl', 'wachtwoord': password})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("www.ichthusculemborg.nl")
    conn.request("POST", "/intranet/login.asp?p=/planner/persons", params, headers)
    response = conn.getresponse()
    if response.status == 302:
        response.read()
        location = response.getheader('location')
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "Cookie": response.getheader('set-cookie')}
        conn.request("GET", location, '', headers)
        response = conn.getresponse()
    else:
        return []
    assert (response.status == 200)
    persons = response.read()
    return json.loads(persons)


def exists(availability, name, task):
    for person in availability:
        if person["name"].replace(' ', '_') == name:
            for task2 in person["tasks"]:
                if task2["task"].replace(' ', '_') == task:
                    return True
    return False


def get_sets(password):
    import requests
    import json
    r = requests.get("http://www.ichthusculemborg.nl/services/commitments",auth=('hans.kalle@telfort.nl', password))
    assert r.status_code == 200
    commitments = json.loads(r.text)
    sets = {}
    for commitment in commitments:
        if not commitment['task'] in sets:
            sets[commitment['task']] = []
        sets[commitment['task']].append(commitment['person'])
    return sets


def show_help():
    print sys.argv[0], ' [-h] [-f <from week>] [-t <till week>]'
    print '\t-f\tFrom week.'
    print '\t-h\tThis help.'
    print '\t-t\tTill week.'


if __name__ == "__main__":
    import sys
    import getopt
    import getpass

    from_week = 40
    till_week = 52
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:t:")
    except getopt.GetoptError:
        print "Incorrect arguments."
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
        print "Till-week must be greater then from-week."
        sys.exit(2)
    password = getpass.getpass('Password for hans.kalle@telfort.nl: ')
    availability = get_availability(password)
    persons = get_persons(password)
    uid_from_name = {}
    for person in persons:
        name = person["name"].replace(' ', '_')
        uid = person["uid"]
        if name not in uid_from_name:
            uid_from_name[name] = uid
    sets = get_sets(password)
    for setname in sets:
        for name in sets[setname]:
            if name not in uid_from_name:
                uid_from_name[name] = get_uid()
    for setname in sets:
        for name in sets[setname]:
            if name not in ["In_de_dienst", "Niemand"]:
                if not exists(availability, name, setname):
                    for week in range(from_week, till_week + 1):
                        print post_availability(uid_from_name[name], name.replace('_', ' '), setname.replace('_', ' '),
                                                week, "yes")
