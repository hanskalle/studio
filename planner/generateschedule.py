#!/usr/bin/env python
import json
from datetime import datetime, date, timedelta, time

import requests

from createmodel import Task, Specials
from services import Services

host = 'www.ichthusculemborg.nl'
auth = ('username', 'password')
base_year = 2016
first_week = 0


def get_last_assignments(events, before_year, before_week, commitments):
    last_assigments = {}
    for event in events:
        eventdate = datetime.strptime(event['start'][:19], '%Y-%m-%dT%H:%M:%S')
        (year, week, weekday) = get_year_week_and_weekday_from_date(eventdate)
        while year < before_year:
            year += 1
            week -= 53
        if week < before_week:
            for assignment in event['assignments']['list']:
                task = assignment['task']
                if task in commitments:
                    person = assignment['person']
                    if person in commitments[task]:
                        if task not in last_assigments:
                            last_assigments[task] = {}
                        last_assigments[task][person] = week
    return last_assigments


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


def write_last_assignments(filename, last_assignments, tasks):
    with open(filename, 'w') as f:
        for task in last_assignments:
            if task[:6] != 'Groep ':
                original_task = task
                if task[:8] == 'Leiding ':
                    task = task[8:]
                if task[:5] == 'Hoofd':
                    task = 'Koster'
                if task[:4] == 'Hulp':
                    task = 'Koster'
                if original_task in tasks:
                    f.write('param ' + original_task.replace(' ', '_') + '_last :=\n')
                    for person in sorted(last_assignments[task].keys()):
                        f.write('\t%s\t%d\n' % (person.replace(' ', '_'), last_assignments[task][person]))
                    f.write(';\n')
        f.write('end;\n')


def write_availabilities(filename, availabilities, tasks):
    count = 0
    with open(filename, 'w') as f:
        f.write("param first_week := 39;\n")
        f.write("param last_week := 64;\n")
        for task in availabilities:
            if task in tasks:
                f.write('param ' + task.replace(' ', '_') + '_available :\n')
                f.write('\t\t\t')
                for week in range(39, 64 + 1):
                    f.write('\t%d' % week)
                f.write(' :=\n')
                for person in sorted(availabilities[task].keys()):
                    f.write('\t%s\t' % person.replace(' ', '_'))
                    for week in range(39, 64 + 1):
                        key = str(week)
                        f.write('\t%s' % availabilities[task][person][key])
                        if availabilities[task][person][key] != '0':
                            count += 1
                    f.write('\n')
                f.write(';\n')
        f.write('end;\n')
        print("Aantal opties:", count)


def write_commitments(filename, commitments, tasks):
    with open(filename, 'w') as f:
        for task, persons in commitments.items():
            if task.replace(' ', '_') in tasks:
                f.write("set %s_persons :=" % task.replace(' ', '_'))
                for person in persons:
                    f.write(" %s" % person.replace(' ', '_'))
                f.write(";\n")
                f.write("param %s_ritme :=\n" % task.replace(' ', '_'))
                for person, frequency in persons.items():
                    f.write("\t%s\t%s\n" % (person.replace(' ', '_'), frequency))
                f.write(";\n")
        f.write('end;\n')


def add_last_assigment(last_assignments, task, person, week):
    if task not in last_assignments:
        last_assignments[task] = {}
    last_assignments[task][person] = week


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


def christmas_on_sunday():
    return date(base_year, 12, 25).weekday() == 6


def get_date_of_sunday_of_week(week):
    if not christmas_on_sunday():
        # Christmas hack
        if not christmas_on_sunday():
            if week == "52":
                return date(base_year, 12, 25)
        elif int(week) >= 53:
            return date(base_year, 1, 1) + timedelta(days=7 * (int(week) - 1)) + timedelta(
                days=date(2016, 1, 1).weekday() - 2)
    # End Christmas hack
    return date(base_year, 1, 1) + timedelta(days=7 * int(week)) + timedelta(days=date(2016, 1, 1).weekday() - 2)


def get_year_week_and_weekday_from_date(eventdate):
    if not christmas_on_sunday():
        # Christmas hack
        if eventdate == datetime(eventdate.year, 12, 25):
            return 52, 0
            # End Christmas hack
    year, week, weekday = eventdate.isocalendar()
    if not christmas_on_sunday():
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


def show_fixes(fixes, sel_task, sel_person):
    for fix in fixes:
        if fix[0] == sel_task and fix[1] == sel_person:
            print(fix)

def get_task_name_list(tasks):
    names = []
    for task in tasks:
        names.append(task.dict['name'])
    return names


def get_results(timlim):
    services = Services('http://www.ichthusculemborg.nl/services', auth)
    availabilities = services.get_availabilities()
    commitments = services.get_commitments()
    last_assignments = get_last_assignments(services.get_events(), base_year, first_week, commitments)

    zangleiding = Task('Zangleiding')

    muziek = Task('Muziek', True)
    muziek.set_essential('Wendy', 5)
    muziek.set_essential('Vena', 5)
    muziek.set_essential('Selicia', 5)
    muziek.set_essential('David', 5)
    muziek.set_essential('Rosalie', 10)
    muziek.set_essential('Xandra', 10)
    muziek.set_team('Tim_alleen', ['Tim'])
    muziek.set_team('Tim', ['Tim', 'Vena', 'Rosalie', 'Xandra'])
    muziek.set_team('Jonathan', ['Jonathan', 'Rosalie', 'Wendy', 'Selicia'])
    muziek.set_team('Johan', ['Johan', 'Hans_Z', 'David'])
    muziek.set_team('Onbezet', ['Onbezet'])

    geluid = Task('Geluid')

    beamer = Task('Beamer')

    leiding_rood = Task('Leiding Rood')

    leiding_wit = Task('Leiding Wit')

    groep_wit = Task('Groep Wit', paired_task='Leiding Wit')

    groep_wit.set_pair('Dieuwke', 'Emma')
    groep_wit.set_pair('Jacolien', 'Esther')
    groep_wit.set_pair('Elsa', 'Esther')
    groep_wit.set_pair('Elsa', 'Ferdinand')
    groep_wit.set_pair('Marian', 'Jannienke')
    groep_wit.set_pair('Lianne', 'Thirza')

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

    welkom = Task('Welkom')

    koffie = Task('Koffie', in_teams=True)
    koffie.set_team('Cafe_Rouler', ['Cafe_Rouler'])
    koffie.set_team('Jacolien', ['Jacolien', 'Miranda'])
    koffie.set_team('Mieke', ['Mieke', 'Emmely'])
    koffie.set_team('Marieke', ['Marieke', 'Ton'])
    koffie.set_team('Monika', ['Monika', 'Rinus'])
    koffie.set_team('Nora', ['Nora', 'Wim_R'])
    koffie.set_team('Dieuwke', ['Dieuwke', 'Hans_M'])

    hoofdkoster = Task('Hoofdkoster', succesive_count=1)

    hulpkoster = Task('Hulpkoster', default_number_needed=2)

    # Einde herfstvakantie
    hulpkoster.set_number_needed(42, 3)  # Matten zuigen

    # Kids Praise 6 november
    leiding_wit.set_number_needed(44, 0)
    groep_wit.set_number_needed(44, 0)
    leiding_blauw.set_number_needed(44, 2)
    groep_blauw.set_number_needed(44, 2)
    hoofdkoster.set_number_needed(44, 2)
    hulpkoster.set_number_needed(44, 4)
    koffie.set_number_needed(44, 2)

    # Kerst
    hoofdkoster.set_number_needed(51, 4)
    hulpkoster.set_number_needed(51, 4)
    leiding_wit.set_number_needed(51, 0)
    groep_wit.set_number_needed(51, 0)
    leiding_blauw.set_number_needed(51, 0)
    groep_blauw.set_number_needed(51, 0)

    # Einde kerstvakantie
    hulpkoster.set_number_needed(53, 3)  # Matten zuigen

    # Einde voorjaarsvakantie
    hulpkoster.set_number_needed(61, 3)  # Matten zuigen

    dont_exclude = [
        ('Beamer', 'Hulpkoster'),
        ('Groep_Blauw', 'Welkom'),
        ('Hulpkoster', 'Welkom'),
        ('Muziek', 'Zangleiding'),
        ('Leiding_Rood', 'Leiding_Wit'),
        ('Gebed', 'Welkom')]

    specials = Specials()
    fixes = []

    # tasks = [gebed]
    # write_last_assignments('last.dat', last_assignments, get_task_name_list(tasks))
    # write_availabilities('availability.dat', availabilities, get_task_name_list(tasks))
    # write_commitments('commitments.dat', commitments, get_task_name_list(tasks))
    # if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
    #     exit(1)
    # return parse_results('results.txt')

    # for task in [zangleiding, muziek, geluid, leiding_rood, leiding_wit, leiding_blauw, beamer, welkom, koffie,
    #              hoofdkoster, gebed, hulpkoster]:
    #     tasks = [task]
    #     if optimize_phase(tasks, dont_exclude, specials, fixes, "10", last_assignments, availabilities, commitments):
    #         exit(1)

    # tasks = [zangleiding, muziek, geluid, leiding_rood, leiding_wit, leiding_blauw, beamer, welkom, koffie,
    #          hoofdkoster, gebed, hulpkoster]
    # if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
    #     exit(1)


    tasks = []

    tasks = [zangleiding, muziek, geluid, hoofdkoster]
    specials.add_constraint("subject to Jolanda_doet_de_Kids_Praise: Zangleiding['Jolanda', 44] = 1;")
    specials.add_var("var hansteveel {weeks}, binary;")
    specials.add_objective_term("500 * (sum {w in weeks} hansteveel[w])")
    specials.add_constraint("subject to Hans_D_niet_3_zondagen_achter_elkaar {w in first_week+2..last_week}:"
                            "(sum {w2 in w-2..w} (  Hoofdkoster['Hans_D',w2] + Geluid['Hans_D',w2]))  <= 2 + hansteveel[w];")
    specials.add_constraint(
        "subject to Een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_eigen_team"
        " {p in Zangleiding_persons inter Muziek_leaders, w in weeks}:"
        " Muziek[p,w] >= Zangleiding[p,w];")
    specials.add_constraint(
        "subject to Liesbeth_Z_minimaal_7_diensten_rust_tussendoor {w in first_week+7..last_week}:"
        " (sum {w2 in w-7..w} Zangleiding['Liesbeth_Z',w2]) <= 1;")
    specials.add_constraint(
        "subject to Liesbeth_Z_maximaal_1_keer_per_8_weken_historisch"
        " {w in Zangleiding_last['Liesbeth_Z']+1..Zangleiding_last['Liesbeth_Z']+7: w >= first_week}:"
        " Zangleiding['Liesbeth_Z',w] = 0;")
    specials.add_constraint(
        "subject to Onbezet_alleen_bij_Ramon_of_Hans_K_Zangleiding {w in (weeks diff {44, 51, 52})}:"
        " Muziek['Onbezet',w] <= (Zangleiding['Hans_K',w] + Zangleiding['Ramon',w]);")
    specials.add_constraint("subject to Gelegenheidsband_bij_Kids_Praise: Muziek['Onbezet',44] = 1;")
    specials.add_constraint("subject to Gelegenheidsband_bij_Kerst: Muziek['Onbezet',51] = 1;")
    if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
        exit(1)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))
    show_fixes(fixes, 'Zangleiding', 'Tim')

    tasks.extend([leiding_rood, leiding_wit, groep_wit, leiding_blauw, groep_blauw])
    specials.add_constraint("subject to Rood_in_de_dienst_bij_Kids_Praise: Leiding_Rood['In_de_dienst',44] = 1;")
    specials.add_constraint("subject to Rood_in_de_dienst_bij_Kerst: Leiding_Rood['In_de_dienst',51] = 1;")
    specials.add_var("var wijngaardenbreuk {weeks}, binary;")
    specials.add_objective_term("40 * (sum {w in weeks} wijngaardenbreuk[w])")
    specials.add_var("var broekhofbreuk {weeks}, binary;")
    specials.add_objective_term("20 * (sum {w in weeks} broekhofbreuk[w])")
    specials.add_constraint("subject to Rood_niet_in_de_dienst_als_Muziek_onbezet_is {w in (weeks diff {44, 51})}:"
                            " Leiding_Rood['In_de_dienst',w] + Muziek['Onbezet',w] <= 1;")
    specials.add_constraint("subject to Mirjam_leidt_groep_Blauw_wanneer_Jan_Martijn_groep_Rood_leidt {w in weeks}:"
                            " Leiding_Rood['Jan_Martijn',w] <= Leiding_Blauw['Mirjam',w] + broekhofbreuk[w];")
    specials.add_constraint("subject to Jan_Martijn_leidt_groep_Rood_wanneer_Mirjam_groep_Blauw_leidt {w in weeks}:"
                            " Leiding_Blauw['Mirjam',w] <= Leiding_Rood['Jan_Martijn',w] + broekhofbreuk[w];")
    specials.add_constraint("subject to Rachel_leidt_groep_Blauw_wanneer_Tim_groep_Rood_leidt {w in weeks}:"
                            " Leiding_Rood['Tim',w] <= Leiding_Blauw['Rachel',w] + wijngaardenbreuk[w];")
    specials.add_constraint("subject to Tim_leidt_groep_Rood_wanneer_Rachel_groep_Blauw_leidt {w in weeks}:"
                            " Leiding_Blauw['Rachel',w] <= Leiding_Rood['Tim',w] + wijngaardenbreuk[w];")
    if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
        exit(1)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([beamer])
    if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
        exit(1)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([welkom, koffie])
    specials.add_var("var matthijszonderlianne {weeks}, binary;")
    specials.add_objective_term("10 * (sum {w in weeks} matthijszonderlianne[w])")
    specials.add_constraint("subject to Als_Matthuis_hoofdkoster_is_doet_Lianne_welkom {w in weeks}:"
                            " Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne[w];")
    specials.add_var("var liannezondermatthijs {weeks}, binary;")
    specials.add_objective_term("20 * (sum {w in weeks} liannezondermatthijs[w])")
    specials.add_constraint("subject to Als_Lianne_welkom_doet_is_Matthijs_hoofdkoster {w in weeks}:"
                            " Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs[w];")
    if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
        exit(1)
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
    if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
        exit(1)
    fixes = get_fixes('results.txt', get_task_name_list(tasks))

    tasks.extend([hulpkoster])
    specials.add_var("var roelhermanbreuk {weeks}, binary;")
    specials.add_objective_term("5 * (sum {w in weeks} roelhermanbreuk[w])")
    specials.add_constraint("subject to Roel_liefst_Hulpkoster_met_Hoofdkoster_Herman_B {w in weeks}:"
                            "Hulpkoster['Roel',w] <= Hoofdkoster['Herman_B',w] + roelhermanbreuk[w];")
    if optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
        exit(1)
    return parse_results('results.txt')


def optimize_phase(tasks, dont_exclude, specials, fixes, timlim, last_assignments, availabilities, commitments):
    import subprocess
    import createmodel
    import os

    print("#### %s ####" % ', '.join(get_task_name_list(tasks)))
    write_last_assignments('last.dat', last_assignments, get_task_name_list(tasks))
    write_availabilities('availability.dat', availabilities, get_task_name_list(tasks))
    write_commitments('commitments.dat', commitments, get_task_name_list(tasks))
    createmodel.Generator(tasks, specials=specials, dont_exclude=dont_exclude, fixes=fixes).write('gen.mod',
                                                                                                  'planner.dat')
    return_code = subprocess.call(
        ['glpsol',
         '--pcost',
         '--tmlim', timlim,
         '--model', 'gen.mod',
         '--data', 'planner.dat',
         '--data', 'commitments.dat',
         '--data', 'last.dat',
         '--data', 'availability.dat',
         '-y', 'results.txt'])
    if return_code == 0:
        size = os.stat('results.txt').st_size
        if size == 0:
            return_code = -1
    return return_code


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
        markup_file.write(rooster[week]['datum'].strftime('%d-%m-%Y'))
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


def find_event(events, eventdate, description):
    start = create_start(eventdate, time(10, 00, 00))
    for event in events:
        if event['start'][:11] == start[:11]:
            if event['description'] == description:
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


def read_passwd(filename):
    with open(filename, 'r') as f:
        passwd = f.read()
    return passwd.strip()


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
        existing_event = find_event(existing_events, eventdate, 'Samenkomst')
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
    # print('\t-a\tGet availability from service.')
    # print('\t-c\tGet commitments from service.')
    # print('\t-l\tGet last assignments from service.')
    print('\t-p\tPublish schedule on service.')
    print('\t-o\tWrite output to this file. Default rooster.txt.')
    print('\t-s\tHostname. Default www.ichthusculemborg.nl.')
    print('\t-t\tLimit search time in seconds. Default 300 seconds.')


if __name__ == "__main__":
    import sys
    import getopt

    auth = ('hans.kalle@telfort.nl', read_passwd('passwd.txt'))

    time_limit = "300"
    # do_get_availability = False
    # do_get_last_assignments = False
    # do_get_commitments = False
    do_publish = False
    output_filename = 'rooster.txt'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "achlo:ps:t:")
    except getopt.GetoptError:
        print("Incorrect arguments.")
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        # if opt == "-a":
        #     do_get_availability = True
        # elif opt == "-c":
        #     do_get_commitments = True
        if opt == '-h':
            show_help()
            sys.exit()
        # elif opt == "-l":
        #     do_get_last_assignments = True
        elif opt == "-o":
            output_filename = arg
        elif opt == "-p":
            do_publish = True
        elif opt == "-s":
            host = arg
        elif opt == "-t":
            time_limit = arg
    # if do_get_availability or do_publish or do_get_last_assignments or do_get_commitments:
    #     auth = ('hans.kalle@telfort.nl', getpass.getpass('Password for hans: '))
    new_rooster = get_results(time_limit)
    write_markup(output_filename, new_rooster)
    if do_publish:
        write_rest(new_rooster)
