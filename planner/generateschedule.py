#!/usr/bin/env python
import json
from datetime import datetime, date, timedelta, time

import requests

host = 'www.ichthusculemborg.nl'
auth = ('username', 'password')
state_value = {'no': '0', 'yes': '1', 'maybe': '.5'}
this_year = 2016
last_year = 2015
first_week = 0


def delete_assignment(uid):
    url = "http://" + host + "/services/assignments/" + uid
    r = requests.delete(url, auth=auth)
    return


def create_event(eventdate, eventtime, description, location, remark):
    url = "http://" + host + "/services/events"
    data = json.dumps({
        "start": create_start(eventdate, eventtime),
        "description": description,
        "location": location,
        "remark": remark})
    print data
    r = requests.post(url, data, auth=auth)
    assert (r.status_code == 200)
    return r.json()


def create_start(eventdate, eventtime):
    return datetime.combine(eventdate, eventtime).isoformat()


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


def get_events():
    url = "http://" + host + "/services/events"
    r = requests.get(url, auth=auth)
    assert (r.status_code == 200)
    return r.json()


def update_last_assignments():
    last_assignments = {}
    events = get_events()
    for event in events:
        for assignment in event['assignments']['list']:
            eventdate = datetime.strptime(event['start'][:19], '%Y-%m-%dT%H:%M:%S')
            year, week, weekday = get_year_week_and_weekday_from_date(eventdate)
            if year < this_year:
                week -= 54
            if week < first_week:
                if (weekday == 7) or (eventdate.month == 12 and eventdate.day == 25):  # Only sunday-tasks or christmas
                    task = assignment['task']
                    person = assignment['person'].replace(' ', '_')
                    if ',' in person:
                        persons = person
                        for person in persons.split(','):
                            person = person.strip()
                            add_last_assigment(last_assignments, task, person, week)
                    else:
                        add_last_assigment(last_assignments, task, person, week)
    availability = get_persons()
    sets = get_sets()
    f = open('last.dat', 'w')
    for task in get_tasks(availability):
        if task[:6] != 'Groep ':
            original_task = task
            if task[:8] == 'Leiding ':
                task = task[8:]
            if task[:5] == 'Hoofd':
                task = 'Koster'
            if task[:4] == 'Hulp':
                task = 'Koster'
            if original_task in sets:
                f.write('param ' + original_task.replace(' ', '_') + '_last default -53 :=\n')
                if task in last_assignments:
                    for person in sorted(last_assignments[task]):
                        if person in sets[original_task]:
                            f.write('\t%s\t%d\n' % (person.replace(' ', '_'), last_assignments[task][person]))
                f.write(';\n')
    f.write('end;\n')
    f.close()


def add_last_assigment(last_assignments, task, person, week):
    if task not in last_assignments:
        last_assignments[task] = {}
    last_assignments[task][person] = week


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
            return task['availability']
    return None


def write_availability(filename, persons):
    sets = get_sets()
    availability_file = open(filename, 'w')
    weeks = get_weeks(persons)
    availability_file.write('param first_week := ' + weeks[0] + ';\n')
    availability_file.write('param last_week := ' + weeks[-1] + ';\n')
    for task in get_tasks(persons):
        if task in sets:
            availability_file.write('param %s_available default 1:\n' % task.replace(' ', '_'))
            for week in weeks:
                availability_file.write(' ')
                availability_file.write(week)
            availability_file.write(':=\n')
            for person in sorted(persons):
                availability = get_availability(person, task)
                name = person['name'].replace(' ', '_')
                if name in sets[task]:
                    if availability is not None:
                        availability_file.write(name)
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
        rooster[week]['missing'] = []
        rooster[week]['rather not'] = []
        rooster[week]['not prefered pair'] = []


def get_date_of_sunday_of_week(week):
    # Christmas hack
    if week == "52":
        return date(2016, 12, 25)
    elif week == "53":
        return date(2016, 1, 1) + timedelta(days=7 * (int(week) - 1)) + timedelta(days=2)
    # End Christmas hack
    return date(2016, 1, 1) + timedelta(days=7 * int(week)) + timedelta(days=2)


def get_year_week_and_weekday_from_date(eventdate):
    # Christmas hack
    if eventdate == datetime(eventdate.year, 12, 25):
        return 52, 0
    # End Christmas hack
    year, week, weekday = eventdate.isocalendar()
    # Christmas hack
    if week >= 52:
        week += 1
    # End Christmas hack
    return year, week, weekday


def add_person(rooster, week, task, person):
    if task not in rooster[week]:
        rooster[week][task] = []
    rooster[week][task].append(person)


def get_sets():
    sets = {}
    complete_line = ''
    for line in open('planner.dat', 'r'):
        if '#' in line:
            line = line[0:line.find('#')]
        complete_line = complete_line + ' ' + line
        complete_line = complete_line.strip()
        if len(complete_line) > 0:
            if complete_line[-1] == ';':
                if complete_line[0:3] == 'set':
                    words = complete_line[4:-1].split()
                    if words[0][-8:] == '_persons':
                        sets[words[0][0:-8].replace('_', ' ')] = words[2:]
                complete_line = ''
    return sets


def get_results(timlim):
    import subprocess
    import createmodel
    createmodel.Generator().write_model('gen.mod')
    subprocess.check_call(
        ['glpsol',
         '--tmlim', timlim,
         '--model', 'gen.mod',
         '--data', 'planner.dat',
         '--data', 'last.dat',
         '--data', 'availability.dat',
         '-y', 'results.txt'])
    return parse_results('results.txt')


def write_markup(filename, rooster):
    markup_file = open(filename, 'w')
    markup_file.write('^week^datum^leiding^team^geluid^beamer^blauw^wit^rood^koffie^welkom^Gebed^koster^opmerkingen^\n')
    weeks = rooster.keys()
    for week in sorted(weeks):
        columns = [['Zangleiding'], ['Muziek'], ['Geluid'], ['Beamer'], ['Leiding Blauw', 'Groep Blauw'],
                   ['Leiding Wit', 'Groep Wit'], ['Leiding Rood', 'Groep Rood'], ['Koffie'], ['Welkom'], ['Gebed'],
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
                    names.extend(rooster[week][task])
            width = 10 * len(column)
            markup_file.write(("{:<" + str(width) + "s}").format(", ".join(names)))
            markup_file.write('|')
        remarks = []
        if len(rooster[week]['missing']) > 0:
            remarks.append(', '.join(rooster[week]['missing']) + ' mist')
        if len(rooster[week]['rather not']) > 0:
            remarks.append(', '.join(rooster[week]['rather not']) + ' liever niet')
        if len(rooster[week]['not prefered pair']):
            remarks.append(', '.join(rooster[week]['not prefered pair']) + ' afwijkend paar')
        if len(remarks) > 0:
            markup_file.write(','.join(remarks))
        markup_file.write(' |\n')
    markup_file.close()
    show_file(filename)


def show_file(filename):
    for line in open(filename, 'r'):
        print line[0:-1]


def find_event(events, eventdate, eventtime):
    start = create_start(eventdate, eventtime)
    for event in events:
        if event['start'] == start:
            return event
    return None


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
        'Gebed': ['Gebed'],
        'Koster': ['Hoofdkoster', 'Hulpkoster']}
    existing_events = get_events()
    weeks = rooster.keys()
    eventtime = time(10, 00, 00)
    for week in sorted(weeks):
        eventdate = get_date_of_sunday_of_week(week)
        existing_event = find_event(existing_events, eventdate, eventtime)
        if existing_event is None:
            event = create_event(eventdate, time(10, 00, 00), 'Samenkomst', 'KJS', '')
            event_uid = event[0]['uid']
        else:
            event_uid = existing_event['uid']
        for assignment, tasks in columns.iteritems():
            if existing_event is not None:
                for existing_assignment in existing_event['assignments']['list']:
                    if existing_assignment['task'] == assignment:
                        delete_assignment(existing_assignment['uid'])
            for task in tasks:
                if task in rooster[week]:
                    for person in rooster[week][task]:
                        if person != 'Niemand':
                            remarks = []
                            if person in rooster[week]['missing']:
                                remarks.append('mist')
                            if person in rooster[week]['rather not']:
                                remarks.append('liever niet')
                            if person in rooster[week]['not prefered pair']:
                                remarks.append('geen voorkeurspaar')
                            create_assignment(event_uid, assignment, person, ', '.join(remarks))


def show_help():
    print sys.argv[0], ' [-alp] [-o <filename>] [-h <hostname>] [-t <time-limit>]'
    print '\t-a\tGet availability from service.'
    print '\t-l\tGet last assignments from service.'
    print '\t-p\tPublish schedule on service.'
    print '\t-o\tWrite output to this file. Default rooster.txt.'
    print '\t-s\tHostname. Default www.ichthusculemborg.nl.'
    print '\t-t\tLimit search time in seconds. Default 300 seconds.'


if __name__ == "__main__":
    import sys
    import getopt
    import getpass

    time_limit = "300"
    do_get_availability = False
    do_get_last_assignments = False
    do_publish = False
    output_filename = 'rooster.txt'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahlo:ps:t:")
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
        elif opt == "-l":
            do_get_last_assignments = True
        elif opt == "-o":
            output_filename = arg
        elif opt == "-p":
            do_publish = True
        elif opt == "-s":
            host = arg
        elif opt == "-t":
            time_limit = arg
    if do_get_availability or do_publish or do_get_last_assignments:
        auth = ('hans.kalle@telfort.nl', getpass.getpass('Password for hans: '))
    if do_get_last_assignments:
        update_last_assignments()
        print 'Laatste inzet opgehaald.'
    if do_get_availability:
        update_availability()
        print 'Beschikbaarheid opgehaald.'
    new_rooster = get_results(time_limit)
    write_markup(output_filename, new_rooster)
    if do_publish:
        write_rest(new_rooster)
