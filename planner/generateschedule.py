#!/usr/bin/env python
import json
from datetime import datetime, date, timedelta, time

import requests

from createmodel import Task, Specials

host = 'www.ichthusculemborg.nl'
auth = ('username', 'password')
state_value = {'no': '0', 'yes': '1', 'maybe': '.5'}
this_year = 2016
last_year = 2015
first_week = 0


def delete_assignment(uid):
    url = "http://" + host + "/services/assignments/" + uid
    r = requests.delete(url, auth=auth)
    assert r.status_code == 200
    return


def create_event(eventdate, eventtime, description, location, remark):
    url = "http://" + host + "/services/events"
    data = json.dumps({
        "start": create_start(eventdate, eventtime),
        "description": description,
        "location": location,
        "remark": remark})
    print(data)
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
    print(data)
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


def update_commitments():
    commitments = get_commitments()
    write_commitments('commitments.dat', commitments)


def get_persons():
    from http.client import HTTPConnection
    from urllib.parse import urlencode
    import json

    params = urlencode({'email': auth[0], 'wachtwoord': auth[1]})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = HTTPConnection("www.ichthusculemborg.nl")
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
    weeks = list(get_weeks(persons))
    availability_file.write('param first_week := ' + weeks[0] + ';\n')
    availability_file.write('param last_week := ' + weeks[-1] + ';\n')
    for task in get_tasks(persons):
        if task in sets:
            availability_file.write('param %s_available:\n' % task.replace(' ', '_'))
            for week in weeks:
                availability_file.write(' ')
                availability_file.write(week)
            availability_file.write(':=\n')
            for person in sorted(persons):
                availability = get_availability(person, task)
                name = person['name']
                if name in sets[task]:
                    name = name.replace(' ', '_')
                    if availability is not None:
                        availability_file.write(name)
                        for available in availability:
                            availability_file.write(' ')
                            availability_file.write(state_value[available['state']])
                        availability_file.write('\n')
            availability_file.write(';\n')
    availability_file.write('end;\n')
    availability_file.close()


def write_commitments(filename, commitments):
    commitments_file = open(filename, 'w')
    tasks = set([commitment['task'] for commitment in commitments])
    for task in tasks:
        commitments_file.write('set %s_persons := ' % task.replace(' ', '_'))
        for commitment in commitments:
            if commitment['task'] == task:
                commitments_file.write(commitment['person'].replace(' ', '_'))
                commitments_file.write(' ')
        commitments_file.write(';\n')
        commitments_file.write('param %s_ritme := \n' % task.replace(' ', '_'))
        for commitment in commitments:
            if commitment['task'] == task:
                commitments_file.write('\t')
                commitments_file.write(commitment['person'].replace(' ', '_'))
                commitments_file.write(' ')
                commitments_file.write(commitment['frequency'])
                commitments_file.write('\n')
        commitments_file.write(';\n')
    commitments_file.write('end;\n')
    commitments_file.close()


def parse_results(filename):
    import re
    pattern = re.compile("(?P<task>[A-Za-z_]+)\[(?P<person>[A-Za-z_]+),(?P<week>[0-9]+)\]\.val = 1")
    rooster = {}
    for line in open(filename):
        if line[-9:-1] == ".val = 1":
            match = pattern.match(line)
            if match:
                values = pattern.match(line).groupdict()
                add_person(rooster, values["week"], values["task"], values["person"])
    return rooster


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
    if week not in rooster:
        rooster[week] = {}
        rooster[week]['datum'] = get_date_of_sunday_of_week(week)
        rooster[week]['missing'] = []
        rooster[week]['rather not'] = []
        rooster[week]['not prefered pair'] = []
    task = task.replace('_', ' ')
    if task not in rooster[week]:
        rooster[week][task] = []
    person = person.replace('_', ' ')
    rooster[week][task].append(person)


def get_commitments():
    import requests
    import json
    r = requests.get("http://" + host + "/services/commitments", auth=auth)
    assert r.status_code == 200
    return json.loads(r.text)


def get_sets():
    sets = {}
    for commitment in get_commitments():
        if not commitment['task'] in sets:
            sets[commitment['task']] = []
        sets[commitment['task']].append(commitment['person'])
    return sets


def get_task_name_list(tasks):
    names = []
    for task in tasks:
        names.append(task.dict['name'])
    return names


def get_results(timlim):
    zangleiding = Task('Zangleiding')
    zangleiding.set_number_needed(37, 0)

    muziek = Task('Muziek', True)
    muziek.set_number_needed(22, 0)
    muziek.set_number_needed(37, 0)
    muziek.set_essential('Wendy', 5)
    muziek.set_essential('Vena', 5)
    muziek.set_essential('Selicia', 5)
    muziek.set_essential('David', 5)
    muziek.set_essential('Rosalie', 10)
    muziek.set_essential('Xandra', 10)
    muziek.set_team('Tim', ['Tim', 'Vena', 'Rosalie', 'Xandra'])
    muziek.set_team('Peter', ['Peter', 'Rosalie', 'Jonathan', 'Wendy'])
    muziek.set_team('Johan', ['Johan', 'Hans_Z', 'David'])
    muziek.set_team('Onbezet', ['Onbezet'])

    geluid = Task('Geluid')
    geluid.set_number_needed(22, 0)
    geluid.set_number_needed(37, 0)

    beamer = Task('Beamer')
    beamer.set_number_needed(37, 0)

    leiding_rood = Task('Leiding Rood')
    leiding_rood.set_number_needed(27, 0)
    leiding_rood.set_number_needed(28, 0)
    leiding_rood.set_number_needed(29, 0)
    leiding_rood.set_number_needed(30, 0)
    leiding_rood.set_number_needed(31, 0)
    leiding_rood.set_number_needed(32, 0)
    leiding_rood.set_number_needed(37, 0)

    leiding_wit = Task('Leiding Wit')
    leiding_wit.set_number_needed(27, 0)
    leiding_wit.set_number_needed(28, 0)
    leiding_wit.set_number_needed(29, 0)
    leiding_wit.set_number_needed(30, 0)
    leiding_wit.set_number_needed(31, 0)
    leiding_wit.set_number_needed(32, 0)
    leiding_wit.set_number_needed(37, 0)

    groep_wit = Task('Groep Wit', paired_task='Leiding Wit')
    groep_wit.set_number_needed(27, 0)
    groep_wit.set_number_needed(28, 0)
    groep_wit.set_number_needed(29, 0)
    groep_wit.set_number_needed(30, 0)
    groep_wit.set_number_needed(31, 0)
    groep_wit.set_number_needed(32, 0)
    groep_wit.set_number_needed(37, 0)
    groep_wit.set_pair('Jacolien', 'Thirza')
    groep_wit.set_pair('Xandra', 'Esther')
    groep_wit.set_pair('Yentl', 'Esther')
    groep_wit.set_pair('Dieuwke', 'Emma')
    groep_wit.set_pair('Lianne', 'David')

    leiding_blauw = Task('Leiding Blauw')

    groep_blauw = Task('Groep Blauw', paired_task='Leiding Blauw')
    groep_blauw.set_pair('Rachel', 'Vivianne')
    groep_blauw.set_pair('Mieke', 'Anneke')
    groep_blauw.set_pair('Annelies', 'Noa')
    groep_blauw.set_pair('Mirjam', 'Selicia')
    groep_blauw.set_pair('Lidian', 'Hanna_Vera')
    groep_blauw.set_pair('Wenny', 'Hanna_Vera')
    groep_blauw.set_pair('Miranda', 'Chiara')

    gebed = Task('Gebed', default_number_needed=2)
    gebed.set_number_needed(37, 0)
    gebed.set_param('min', {'Wenny': 3, 'Jan_P': 3})
    gebed.set_param('max', {'Wenny': 3, 'Jan_P': 3})

    welkom = Task('Welkom')
    welkom.set_number_needed(37, 0)
    welkom.set_param('min', {'Wenny': 3})
    welkom.set_param('max', {'Wenny': 3})

    koffie = Task('Koffie', in_teams=True)
    koffie.set_number_needed(35, 2)
    koffie.set_number_needed(37, 0)
    koffie.set_team('Cafe_Roulez', ['Cafe_Roulez'])
    koffie.set_team('Jacolien', ['Jacolien', 'Miranda'])
    koffie.set_team('Mieke', ['Mieke', 'Lydia', 'Emmely'])
    koffie.set_team('Marieke', ['Marieke', 'Ton'])
    koffie.set_team('Monika', ['Monika', 'Rinus'])
    koffie.set_team('Nora', ['Nora', 'Wim_R'])
    koffie.set_team('Dieuwke', ['Dieuwke', 'Hans_M'])

    hoofdkoster = Task('Hoofdkoster', succesive_count=2)
    # hoofdkoster.set_number_needed(37, 0) Geeft problemen met het tweemaal achtereenvolgens inzetten...

    hulpkoster = Task('Hulpkoster', default_number_needed=2)
    hulpkoster.set_number_needed(16, 6)
    hulpkoster.set_number_needed(18, 3)
    hulpkoster.set_number_needed(27, 0)
    hulpkoster.set_number_needed(28, 0)
    hulpkoster.set_number_needed(29, 0)
    hulpkoster.set_number_needed(30, 0)
    hulpkoster.set_number_needed(31, 0)
    hulpkoster.set_number_needed(32, 0)
    hulpkoster.set_number_needed(33, 3)
    hulpkoster.set_number_needed(35, 3)
    hulpkoster.set_number_needed(37, 0)
    hulpkoster.set_param('min', {'Levi': 1})
    hulpkoster.set_param('max', {'Levi': 2})

    dont_exclude = [
        ('Beamer', 'Hulpkoster'),
        ('Beamer', 'Gebed'),
        ('Groep_Blauw', 'Welkom'),
        ('Hulpkoster', 'Welkom'),
        ('Leiding_Blauw', 'Welkom'),
        ('Muziek', 'Zangleiding'),
        ('Leiding_Rood', 'Leiding_Wit'),
        ('Geluid', 'Hoofdkoster'),
        ('Gebed', 'Welkom')]

    specials = Specials()

    tasks = [zangleiding, muziek, geluid]
    specials.add_constraint(
        "subject to Een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_eigen_team"
        " {p in Zangleiding_persons inter Muziek_leaders, w in weeks}:"
        " Muziek[p,w] >= Zangleiding[p,w];")
    specials.add_constraint("subject to jeugddienst1: Zangleiding['Jolanda',22] = 1;")
    optimize_phase('1', tasks, dont_exclude, specials, [], timlim)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([leiding_rood, leiding_wit, groep_wit, leiding_blauw, groep_blauw])
    specials.ignore_constraint("minimum_.*")
    specials.add_constraint("subject to jeugddienst2: Leiding_Rood['In_de_dienst',22] = 1;")
    specials.add_constraint("subject to Wenny_Blauw_1: Leiding_Blauw['Wenny',14] = 1;")
    specials.add_constraint("subject to Wenny_Blauw_2: Leiding_Blauw['Wenny',18] = 1;")
    specials.add_var("var wijngaardenbreuk {weeks}, binary;")
    specials.add_objective_term("8 * (sum {w in weeks} wijngaardenbreuk[w])")
    specials.add_constraint("subject to Rachel_leidt_groep_Blauw_wanneer_Tim_groep_Rood_leidt {w in weeks}:"
                            " Leiding_Rood['Tim',w] <= Leiding_Blauw['Rachel',w] + wijngaardenbreuk[w];")
    specials.add_constraint("subject to Tim_leidt_groep_Rood_wanneer_Rachel_groep_Blauw_leidt {w in weeks}:"
                            " Leiding_Blauw['Rachel',w] <= Leiding_Rood['Tim',w] + wijngaardenbreuk[w];")
    optimize_phase('2', tasks, dont_exclude, specials, fixes, timlim)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([beamer, welkom, koffie, hoofdkoster])
    specials.add_constraint("subject to Bas_tot_vakantie_alleen_beamer_als_Rood_in_de_dienst {w in weeks: w < 27}:"
                            " Beamer['Bas',w] <= Leiding_Rood['In_de_dienst',w];")
    specials.add_var("var matthijszonderlianne, binary;")
    specials.add_objective_term("10 * matthijszonderlianne")
    specials.add_constraint("subject to Als_Matthuis_hoofdkoster_is_doet_Lianne_welkom {w in weeks}:"
                            " Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne;")
    specials.add_var("var liannezondermatthijs, binary;")
    specials.add_objective_term("20 * liannezondermatthijs")
    specials.add_constraint("subject to Als_Lianne_welkom_doet_is_Matthijs_hoofdkoster {w in weeks}:"
                            " Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs;")
    specials.add_constraint("subject to Wenny_Welkom_1: Welkom['Wenny',13] = 1;")
    specials.add_constraint("subject to Wenny_Welkom_2: Welkom['Wenny',17] = 1;")
    specials.add_constraint("subject to Wenny_Welkom_3: Welkom['Wenny',19] = 1;")
    specials.add_constraint("subject to cafe_roulez1: Koffie['Cafe_Roulez', 21] = 1;")
    specials.add_constraint("subject to cafe_roulez2: Koffie['Cafe_Roulez', 38] = 1;")
    optimize_phase('3', tasks, dont_exclude, specials, fixes, timlim)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([gebed])
    specials.add_var("set gebedsmannen := {'Hans_Z', 'Hans_K', 'Wim_R', 'Andreas', 'Roeland', 'Jan_P'};")
    specials.add_constraint("subject to Rachel_geen_gebed_met_man {w in weeks}:"
                            " Gebed['Rachel',w] <= 1 - (sum {p in gebedsmannen} Gebed[p,w]);")
    specials.add_constraint("subject to Rachel_geen_gebed_als_Tim_een_taak_heeft {w in weeks}:"
                            " Gebed['Rachel',w] <= 1 - Muziek['Tim',w] - Leiding_Rood['Tim',w];")
    specials.add_constraint("subject to Geen_mannen_samen_gebed {w in weeks}:"
                            " (sum {p in gebedsmannen} Gebed[p,w]) <= 1;")
    specials.add_constraint("subject to Nora_gebed_met_Wim_R {w in weeks}:"
                            " Gebed['Nora',w] <= Gebed['Wim_R',w];")
    specials.add_constraint("subject to Liesbeth_Z_gebed_met_Hans_Z {w in weeks}:"
                            " Gebed['Liesbeth_Z',w] <= Gebed['Hans_Z',w];")
    specials.add_constraint("subject to Wenny_gebed_met_Jan_P {w in weeks}:"
                            " Gebed['Wenny',w] <= Gebed['Jan_P',w];")
    specials.add_constraint("subject to Wenny_Gebed_1: Gebed['Wenny',13] = 1;")
    specials.add_constraint("subject to Wenny_Gebed_2: Gebed['Wenny',17] = 1;")
    specials.add_constraint("subject to Wenny_Gebed_3: Gebed['Wenny',19] = 1;")
    optimize_phase('4', tasks, dont_exclude, specials, fixes, timlim)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([hulpkoster])
    # specials.add_constraint("subject to Jolanda_geen_zangleiding_tegelijkertijd_met_Wim_A_hulpkoster {w in weeks}:"
    #                         " Zangleiding['Jolanda',w] + Hulpkoster['Wim_A',w] <= 1;")
    # specials.add_constraint("subject to Roel_hulpkoster_met_hoofdkoster_Herman {w in weeks}:"
    #                         " Hulpkoster['Roel',w] <= Hoofdkoster['Herman',w];")
    optimize_phase('', tasks, dont_exclude, specials, fixes, timlim)
    return parse_results('results.txt')


def optimize_phase(phase, tasks, dont_exclude, specials, fixes, timlim):
    import subprocess
    import createmodel

    print("################## Phase %s ##################" % phase)
    createmodel.Generator(tasks, specials=specials, dont_exclude=dont_exclude, fixes=fixes).write('gen.mod',
                                                                                                  'planner.dat')
    subprocess.check_call(
        ['glpsol',
         '--tmlim', timlim,
         '--model', 'gen.mod',
         '--data', 'planner.dat',
         '--data', 'commitments%s.dat' % phase,
         '--data', 'last%s.dat' % phase,
         '--data', 'availability%s.dat' % phase,
         '-y', 'results.txt'])


def write_markup(filename, rooster):
    markup_file = open(filename, 'w')
    markup_file.write('week,datum,leiding,team,geluid,beamer,blauw,wit,rood,koffie,welkom,Gebed,koster,opmerkingen\n')
    weeks = rooster.keys()
    for week in sorted(weeks):
        columns = [['Zangleiding'], ['Muziek present'], ['Geluid'], ['Beamer'], ['Leiding Blauw', 'Groep Blauw'],
                   ['Leiding Wit', 'Groep Wit'], ['Leiding Rood'], ['Koffie present'], ['Welkom'], ['Gebed'],
                   ['Hoofdkoster', 'Hulpkoster']]
        markup_file.write('week ')
        markup_file.write(week)
        markup_file.write(',')
        markup_file.write(rooster[week]['datum'].strftime('%d-%M-%Y'))
        markup_file.write(',')
        for column in columns:
            names = []
            for task in column:
                if task in rooster[week]:
                    names.extend(rooster[week][task])
            markup_file.write("+".join(names))
            markup_file.write(',')
        remarks = []
        if len(rooster[week]['missing']) > 0:
            remarks.append('|'.join(rooster[week]['missing']) + ' mist')
        if len(rooster[week]['rather not']) > 0:
            remarks.append('|'.join(rooster[week]['rather not']) + ' liever niet')
        if len(rooster[week]['not prefered pair']):
            remarks.append('|'.join(rooster[week]['not prefered pair']) + ' afwijkend paar')
        if len(remarks) > 0:
            markup_file.write('|'.join(remarks))
        markup_file.write('\n')
    markup_file.close()
    show_file(filename)


def show_file(filename):
    for line in open(filename, 'r'):
        print(line[0:-1])


def find_event(events, eventdate, eventtime):
    start = create_start(eventdate, eventtime)
    for event in events:
        if event['start'] == start:
            return event
    return None


def get_fixes(file_in, tasks):
    fixes = []
    for line in open(file_in, 'r'):
        line = line.strip()
        if line[-8:] == '.val = 1':
            name = line[:line.find('[')]
            if name in tasks:
                pos1 = line.find('[')
                pos2 = line.find(',')
                task = line[:pos1]
                person = line[pos1 + 1:pos2]
                week = line[pos2 + 1:-9]
                fixes.append((task, person, week))
    return fixes


def write_rest(rooster):
    columns = {
        'Zangleiding': ['Zangleiding'],
        'Muziek': ['Muziek present'],
        'Geluid': ['Geluid'],
        'Beamer': ['Beamer'],
        'Blauw': ['Leiding Blauw', 'Groep Blauw'],
        'Wit': ['Leiding Wit', 'Groep Wit'],
        'Rood': ['Leiding Rood'],
        'Koffie': ['Koffie present'],
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
        for assignment, tasks in columns.items():
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
    print(sys.argv[0], ' [-aclp] [-o <filename>] [-h <hostname>] [-t <time-limit>]')
    print('\t-a\tGet availability from service.')
    print('\t-c\tGet commitments from service.')
    print('\t-l\tGet last assignments from service.')
    print('\t-p\tPublish schedule on service.')
    print('\t-o\tWrite output to this file. Default rooster.txt.')
    print('\t-s\tHostname. Default www.ichthusculemborg.nl.')
    print('\t-t\tLimit search time in seconds. Default 300 seconds.')


if __name__ == "__main__":
    import sys
    import getopt
    import getpass

    time_limit = "300"
    do_get_availability = False
    do_get_last_assignments = False
    do_get_commitments = False
    do_publish = False
    output_filename = 'rooster.txt'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "achlo:ps:t:")
    except getopt.GetoptError:
        print("Incorrect arguments.")
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-a":
            do_get_availability = True
        elif opt == "-c":
            do_get_commitments = True
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
    if do_get_availability or do_publish or do_get_last_assignments or do_get_commitments:
        auth = ('hans.kalle@telfort.nl', getpass.getpass('Password for hans: '))
    if do_get_last_assignments:
        update_last_assignments()
        print('Laatste inzet opgehaald.')
    if do_get_availability:
        update_availability()
        print('Beschikbaarheid opgehaald.')
    if do_get_commitments:
        update_commitments()
        print('Inzet opgehaald.')
    new_rooster = get_results(time_limit)
    write_markup(output_filename, new_rooster)
    if do_publish:
        write_rest(new_rooster)
