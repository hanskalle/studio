#!/usr/bin/env python
from datetime import date, timedelta

def get_persons():
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
            return task['availability'];
    return None

def write_beschikbaarheid(filename, persons):
    state_value = { 'no': '0', 'yes': '1', 'maybe': '.5' }
    file = open(filename, 'w')
    weeks = get_weeks(persons)
    file.write('param first_week := ' + weeks[0] + ';\n')
    file.write('param last_week := ' + weeks[-1] + ';\n')
    for task in get_tasks(persons):
        file.write('param %s_available default 1:\n' % task.replace(' ', '_'))
        for week in weeks:
            file.write(' ')
            file.write(week)
        file.write(':=\n')        
        for person in sorted(persons):
            availability = get_availability(person, task);
            if availability != None:
                file.write(person['name'].replace(' ', '_'))
                for available in availability:
                    file.write(' ')
                    file.write(state_value[available['state']]);
                file.write('\n')
        file.write(';\n')
    file.write('end;\n')
    file.close()
    
def parse_results(filename):
    rooster = {}
    for line in open(filename):
        if 'w = ' in line:
            week = line.strip()[4:]
            if not week in rooster:
                rooster[week] = {}
                rooster[week]['datum'] = date(2015,1,4) + timedelta((int(week)-1) * 7) 
        elif ' = ' in line:
            fields = line.strip().split(' = ')
            task = fields[0][0:-1].replace('_', ' ')
            person = fields[1].replace('_', ' ')
            if task in rooster[week]:
                rooster[week][task] += ', ' + person
            else:
                rooster[week][task] = person
    return rooster

def get_results(persons):
    import subprocess
    write_beschikbaarheid('beschikbaarheid.dat', persons)
    subprocess.check_call(['glpsol','--tmlim','300','--model','gen.mod','--data','planner.dat','--data','beschikbaarheid.dat','-y','results.txt'])
    return parse_results('results.txt')
    
def write_markup(filename, rooster):
    file = open(filename, 'w')
    file.write('^week^datum^leiding^team^geluid^beamer^blauw^wit^rood^koffie^koster^welkom^opmerkingen^\n')
    weeks = rooster.keys()
    for week in sorted(weeks):
        file.write('|week ')
        file.write(week)
        file.write('|')
        file.write(rooster[week]['datum'].strftime('%d %b'))
        file.write('|')
        file.write("{:<9s}".format(rooster[week]['Zangleiding']))
        file.write('|')
        file.write("{:<8s}".format(rooster[week]['Muziek']))
        file.write('|')
        file.write("{:<8s}".format(rooster[week]['Geluid']))
        file.write('|')
        file.write("{:<8s}".format(rooster[week]['Beamer']))
        file.write('|')
        file.write("{:<8s}".format(rooster[week]['Leiding Blauw']))
        file.write(' & ')
        file.write("{:<8s}".format(rooster[week]['Groep Blauw']))
        file.write('|')
        file.write("{:<8s}".format(rooster[week]['Leiding Wit']))
        file.write(' & ')
        file.write("{:<8s}".format(rooster[week]['Groep Wit']))
        file.write('|')
        file.write("{:<11s}".format(rooster[week]['Leiding Rood']))
        file.write('|')
        file.write("{:<9s}".format(rooster[week]['Koffie']))
        file.write('|')
        file.write("{:<8s}".format(rooster[week]['Hoofdkoster']))
        file.write(' & ')
        file.write("{:<16s}".format(rooster[week]['Hulpkoster']))
        file.write('|')
        file.write("{:<16s}".format(rooster[week]['Welkom']))
        file.write('|')
        remarks = []
        if 'missing' in rooster[week]:
            remarks.append(rooster[week]['missing'] + ' mist')
        if 'rather not' in rooster[week]:
            remarks.append(rooster[week]['rather not'] + ' liever niet')
        if 'not prefered pair' in rooster[week]:
            remarks.append(rooster[week]['not prefered pair'] + ' afwijkend paar')
        if len(remarks) > 0:
            file.write(','.join(remarks))
        file.write(' |\n')
    file.close()
    for line in open(filename, 'r'):
        print line[0:-1]

persons = get_persons()
rooster = get_results(persons)
write_markup('rooster.txt', rooster)
