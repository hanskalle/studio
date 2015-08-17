#!/usr/bin/env python
import json
from datetime import datetime, date, timedelta, time

import requests

host = 'www.ichthusculemborg.nl'
auth = ('username', 'password')
state_value = {'no': '0', 'yes': '1', 'maybe': '.5'}


def create_event(date, time, description, location, remark):
    url = "http://" + host + "/services/events"
    data = json.dumps({
        "start": datetime.combine(date, time).isoformat(),
        "description": description,
        "location": location,
        "remark": remark})
    print data
    r = requests.post(url, data, auth=auth)
    assert (r.status_code == 200)
    return r.json()


def create_assignment(event, task, person, remark):
    url = "http://" + host + "/services/events/" + event + "/assignments"
    data = json.dumps({
        "task": task,
        "person": person,
        "remark": remark})
    print data
    r = requests.post(url, data, auth=auth)
    assert (r.status_code == 200)
    return r.json()


def update_availability():
    persons = get_persons()
    write_availability('availability.dat', persons)


def get_persons():
    import httplib
    import urllib
    import json

    params = urllib.urlencode({'email': auth[0], 'wachtwoord': auth[1]})
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


def get_weeks(persons):
    return map(lambda x: x['week'], persons[0]['tasks'][0]['availability'])


def get_tasks(persons):
    tasks = []
    for person in persons:
        for task in person['tasks']:
            if not task['task'] in tasks:
                tasks.append(task['task'])
    return sorted(tasks)


def get_availability(person, taskname):
    for task in person['tasks']:
        if task['task'] == taskname:
            total = 0
            for week in task['availability']:
                total += float(state_value[week['state']])
            if total > 0.0:
                return task['availability']
            else:
                return None
    return None


def write_availability(filename, persons):
    availability_file = open(filename, 'w')
    weeks = get_weeks(persons)
    availability_file.write('param first_week := ' + weeks[0] + ';\n')
    availability_file.write('param last_week := ' + weeks[-1] + ';\n')
    for task in get_tasks(persons):
        availability_file.write('param %s_available default 1:\n' % task.replace(' ', '_'))
        for week in weeks:
            availability_file.write(' ')
            availability_file.write(week)
        availability_file.write(':=\n')
        for person in sorted(persons):
            availability = get_availability(person, task)
            if availability is not None:
                availability_file.write(person['name'].replace(' ', '_'))
                for available in availability:
                    availability_file.write(' ')
                    availability_file.write(state_value[available['state']])
                availability_file.write('\n')
        availability_file.write(';\n')
    availability_file.write('end;\n')
    availability_file.close()


def parse_results(filename):
    rooster = {}
    week = 0
    for line in open(filename):
        if 'w = ' in line:
            week = line.strip()[4:]
            add_week(rooster, week)
        elif ' = ' in line:
            fields = line.strip().split(' = ')
            task = fields[0][0:-1].replace('_', ' ')
            person = fields[1].replace('_', ' ')
            add_person(rooster, week, task, person)
    return rooster


def add_week(rooster, week):
    if week not in rooster:
        rooster[week] = {}
        rooster[week]['datum'] = get_date_of_sunday_of_week(week)


def get_date_of_sunday_of_week(week):
    if week == "52":
        return date(2015, 12, 25)
    elif week == "53":
        return date(2015, 1, 1) + timedelta(days=7 * (int(week) - 1)) + timedelta(days=-4)
    return date(2015, 1, 1) + timedelta(days=7 * int(week)) + timedelta(days=-4)


def add_person(rooster, week, task, person):
    if task in rooster[week]:
        rooster[week][task] += ', ' + person
    else:
        rooster[week][task] = person


def get_results(timlim):
    import subprocess
    import createmodel
    createmodel.Generator().write_model('gen.mod')
    subprocess.check_call(
        ['glpsol', '--tmlim', timlim, '--model', 'gen.mod', '--data', 'planner.dat', '--data', 'last.dat', '--data', 'availability.dat',
         '-y', 'results.txt'])
    return parse_results('results.txt')


def write_markup(filename, rooster):
    markup_file = open(filename, 'w')
    markup_file.write('^week^datum^leiding^team^geluid^beamer^blauw^wit^rood^koffie^welkom^koster^opmerkingen^\n')
    weeks = rooster.keys()
    for week in sorted(weeks):
        columns = [['Zangleiding'], ['Muziek'], ['Geluid'], ['Beamer'], ['Leiding Blauw', 'Groep Blauw'],
                   ['Leiding Wit', 'Groep Wit'], ['Leiding Rood', 'Groep Rood'], ['Koffie'], ['Welkom'],
                   ['Hoofdkoster', 'Hulpkoster']]
        markup_file.write('|week ')
        markup_file.write(week)
        markup_file.write('|')
        markup_file.write(rooster[week]['datum'].strftime('%d %b'))
        markup_file.write('|')
        for column in columns:
            names = []
            for task in column:
                if task in rooster[week]:
                    names.append(rooster[week][task])
            width = 10 * len(column)
            markup_file.write(("{:<" + str(width) + "s}").format(", ".join(names)))
            markup_file.write('|')
        remarks = []
        if 'missing' in rooster[week]:
            remarks.append(rooster[week]['missing'] + ' mist')
        if 'rather not' in rooster[week]:
            remarks.append(rooster[week]['rather not'] + ' liever niet')
        if 'not prefered pair' in rooster[week]:
            remarks.append(rooster[week]['not prefered pair'] + ' afwijkend paar')
        if len(remarks) > 0:
            markup_file.write(','.join(remarks))
        markup_file.write(' |\n')
    markup_file.close()
    show_file(filename)


def show_file(filename):
    for line in open(filename, 'r'):
        print line[0:-1]


def write_rest(rooster):
    columns = {
        'Zangleiding': ['Zangleiding'],
        'Muziek': ['Muziek'],
        'Geluid': ['Geluid'],
        'Beamer': ['Beamer'],
        'Blauw': ['Leiding Blauw', 'Groep Blauw'],
        'Wit': ['Leiding Wit', 'Groep Wit'],
        'Rood': ['Leiding Rood', 'Groep Rood'],
        'Koffie': ['Koffie'],
        'Welkom': ['Welkom'],
        'Koster': ['Hoofdkoster', 'Hulpkoster']}
    weeks = rooster.keys()
    for week in sorted(weeks):
        sunday = get_date_of_sunday_of_week(week)
        event = create_event(sunday, time(10, 00, 00), 'Samenkomst', 'KJS', '')
        event_uid = event[0]['uid']
        for assignment, tasks in columns.iteritems():
            names = []
            for task in tasks:
                if task in rooster[week]:
                    if rooster[week][task] != 'Niemand':
                        names.append(rooster[week][task])
            create_assignment(event_uid, assignment, ", ".join(names), '')


def show_help():
    print sys.argv[0], ' [-ap] [-o <filename>] [-t <time-limit>]'
    print '\t-a\tGet availability from service.'
    print '\t-o\tWrite output to this file. Default rooster.txt.'
    print '\t-p\tPublish schedule on service.'
    print '\t-s\tHostname. Default www.ichthusculemborg.nl.'
    print '\t-t\tLimit search time in seconds. Default 300 seconds.'


if __name__ == "__main__":
    import sys
    import getopt
    import getpass

    time_limit = "300"
    do_get_availability = False
    do_publish = False
    output_filename = 'rooster.txt'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "aho:ps:t:")
    except getopt.GetoptError:
        print "Incorrect arguments."
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-a":
            do_get_availability = True
        elif opt == '-h':
            show_help()
            sys.exit()
        elif opt == "-o":
            output_filename = arg
        elif opt == "-p":
            do_publish = True
        elif opt == "-s":
            host = arg
        elif opt == "-t":
            time_limit = arg
    if do_get_availability or do_publish:
        auth = ('hans.kalle@telfort.nl', getpass.getpass('Password for hans: '))
    if do_get_availability:
        update_availability()
    new_rooster = get_results(time_limit)
    write_markup(output_filename, new_rooster)
    if do_publish:
        write_rest(new_rooster)
