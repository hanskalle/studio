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

sets = get_sets()
uid_from_name = {}
for setname in sets:
    print setname
    for name in sets[setname]:
        if not name in uid_from_name:
            uid_from_name[name] = get_uid()
for setname in sets:
    for name in sets[setname]:
        for week in range(27,27+13):
            print post_availability(uid_from_name[name], name.replace('_',' '), setname.replace('_',' '), week, "yes")