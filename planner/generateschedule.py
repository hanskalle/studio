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
            total = 0
            state_value = { 'no': 0.0, 'yes': 1.0, 'maybe': 0.5 }
            for week in task['availability']:
                total += state_value[week['state']]
            if total > 0.0:
                return task['availability'];
            else:
                return None
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

def get_results(persons, timlim):
    import subprocess
    write_beschikbaarheid('beschikbaarheid.dat', persons)
    subprocess.check_call(['glpsol','--tmlim',timlim,'--model','gen.mod','--data','planner.dat','--data','beschikbaarheid.dat','-y','results.txt'])
    return parse_results('results.txt')
    
def write_markup(filename, rooster):
    file = open(filename, 'w')
    file.write('^week^datum^leiding^team^geluid^beamer^blauw^wit^rood^koffie^welkom^koster^opmerkingen^\n')
    weeks = rooster.keys()
    for week in sorted(weeks):
        columns = [['Zangleiding'],['Muziek'],['Geluid'],['Beamer'],['Leiding Blauw','Groep Blauw'],['Leiding Wit','Groep Wit'],['Leiding Rood','Groep Rood'],['Koffie'],['Welkom'],['Hoofdkoster','Hulpkoster']] 
        file.write('|week ')
        file.write(week)
        file.write('|')
        file.write(rooster[week]['datum'].strftime('%d %b'))
        file.write('|')
        for column in columns:
            names = []
            for task in column:
                if task in rooster[week]:
                    names.append(rooster[week][task])
            width = 10 * len(column)
            file.write(("{:<"+str(width)+"s}").format(", ".join(names)))
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        timlim = sys.argv[1]
    else:
        timlim = '300'
    persons = get_persons()
    rooster = get_results(persons, timlim)
    write_markup('rooster.txt', rooster)
