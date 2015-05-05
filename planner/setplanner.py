#!/usr/bin/env python
from datetime import date, timedelta
import string

def get_uid(size=32, chars=string.digits+"ABCDEF"):
    import random
    return ''.join(random.choice(chars) for _ in range(size))

def post_availability(uid,name,task,week,state):
    import httplib, urllib
    conn = httplib.HTTPConnection("ichthusculemborg.nl")
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "application/json"}
    params = urllib.urlencode({'uid': uid, 'name': name, 'task': task, 'week': week, 'state': state})
    conn.request("POST", "/planner/persons", params, headers)
    response = conn.getresponse()
    assert(response.status==200)
    result = response.read()
    conn.close()
    return result

def get_persons():
    import httplib, urllib, json, getpass
    params = urllib.urlencode({'email': 'hans.kalle@telfort.nl', 'wachtwoord': getpass.getpass()})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("www.ichthusculemborg.nl")
    conn.request("POST", "/intranet/login.asp?p=/planner/ready", params, headers)
    response = conn.getresponse()
    if response.status == 302:
        response.read()
        location = response.getheader('location');
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "Cookie": response.getheader('set-cookie')}
        conn.request("GET", location, '', headers)
        response = conn.getresponse()
    else:
        return []
    assert(response.status==200)
    persons = response.read()
    return json.loads(persons)

def get_availability():
    import httplib, urllib, json, getpass
    params = urllib.urlencode({'email': 'hans.kalle@telfort.nl', 'wachtwoord': getpass.getpass()})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("www.ichthusculemborg.nl")
    conn.request("POST", "/intranet/login.asp?p=/planner/persons", params, headers)
    response = conn.getresponse()
    if response.status == 302:
        response.read()
        location = response.getheader('location');
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain",
                   "Cookie": response.getheader('set-cookie')}
        conn.request("GET", location, '', headers)
        response = conn.getresponse()
    else:
        return []
    assert(response.status==200)
    persons = response.read()
    return json.loads(persons)
    
def exists(availability, name, task):
    for person in availability:
        if person["name"].replace(' ','_') == name:
            for task2 in person["tasks"]:
                if task2["task"].replace(' ','_') == task:
                    return True
    return False
    
def get_sets():
    sets = {}
    complete_line = ''
    for line in open('planner.dat', 'r'):
        complete_line = complete_line + ' ' + line
        complete_line = complete_line.strip()
        if len(complete_line) > 0:
            if complete_line[-1] == ';':
                if complete_line[0:3] == 'set':
                    words = complete_line[4:-1].split()
                    if words[0][-8:] == '_persons':
                        sets[words[0][0:-8]] = words[2:]
                complete_line = ''
    return sets

availability = get_availability()
persons = get_persons()
uid_from_name = {}
for person in persons:
    name = person["name"].replace(' ','_')
    uid = person["uid"]
    if not name in uid_from_name:
        uid_from_name[name] = uid
sets = get_sets()
for setname in sets:
    for name in sets[setname]:
        if not name in uid_from_name:
            uid_from_name[name] = get_uid()
for setname in sets:
    for name in sets[setname]:
        if not exists(availability, name, setname):
            for week in range(27,27+13):
                print post_availability(uid_from_name[name], name.replace('_',' '), setname.replace('_',' '), week, "yes")
