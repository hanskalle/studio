#!/usr/bin/env python
from datetime import date, timedelta

def get_page():
    import httplib, urllib
    params = urllib.urlencode({'u': 'rooster', 'p': 'rooster', 'r': '0'})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("johankn146.146.axc.nl")
    conn.request("POST", "/wiki/doku.php?id=aanbidding:roosteren", params, headers)
    response = conn.getresponse()
    assert(response.status==200)
    page = response.read()
    conn.close()
    return page

def parse_table(page):
    o = False
    n = 0
    beschikbaarheid = {}
    lines = page.split('\n')
    for line in lines:
        if '</table' in line:
            break
        if '<table' in line:
            o = True
        if o:
            if '<td' in line:
                data = parse_row(line)
                beschikbaarheid[data[0]] = data[1:-1]
            if 'week' in line:
                data = parse_row(line)
                beschikbaarheid[data[0]] = data[1:-1]
    return beschikbaarheid

def parse_row(line):
    data = []
    o = False
    f = ''
    for c in line:
        if c == '<':
            o = False
            if len(f) > 0:
                data.append(f.strip())
                f = ''
        if o:
            f += c
        if c == '>':
            o = True
    return data
    
def write_beschikbaarheid(filename, beschikbaarheid):
    file = open(filename, 'w')
    file.write('param eerste_week := ' + min(beschikbaarheid['week']) + ';\n')
    file.write('param laatste_week := ' + max(beschikbaarheid['week']) + ';\n')
    file.write('param beschikbaar default 1:\n')
    for week in beschikbaarheid['week']:
        file.write(' ')
        file.write(week)
    file.write(':=\n')        
    for teamlid in sorted(beschikbaarheid):
        if teamlid != 'week':
            file.write(teamlid.lower())
            for beschikbaar in beschikbaarheid[teamlid]:
                file.write(' ')
                if beschikbaar == 'x':
                    file.write('0')
                if beschikbaar == '':
                    file.write('1')
                if beschikbaar == '-':
                    file.write('.5')
            file.write('\n')
    file.write(';\n')
    file.write('end;\n')
    file.close()
    
def parse_results(filename):
    rooster = {}
    for line in open(filename):
        if 'z = ' in line:
            week = line.strip()[4:]
            if not week in rooster:
                rooster[week] = {}
                rooster[week]['datum'] = date(2015,1,4) + timedelta((int(week)-1) * 7) 
        elif ' = ' in line:
            fields = line.strip().split(' = ')
            if fields[0] in rooster[week]:
                rooster[week][fields[0]] += ', ' + fields[1]
            else:
                rooster[week][fields[0]] = fields[1]
    return rooster

def get_results(beschikbaarheid):
    import subprocess
    write_beschikbaarheid('beschikbaarheid.dat', beschikbaarheid)
    subprocess.check_call(['glpsol','--model','planner.mod','--data','planner.dat','--data','beschikbaarheid.dat','-y','results.txt'])
    return parse_results('results.txt')
    
def write_markup(filename, rooster):
    file = open(filename, 'w')
    file.write('^week^datum^leiding^team^geluid^beamer^blauw^opmerkingen^\n')
    weeks = rooster.keys()
    for week in sorted(weeks):
        file.write('|week ')
        file.write(week)
        file.write('|')
        file.write(rooster[week]['datum'].strftime('%d %b'))
        file.write('|')
        file.write(rooster[week]['leider'])
        file.write('|')
        file.write(rooster[week]['team'])
        file.write('|')
        file.write(rooster[week]['schuiver'])
        file.write('|')
        file.write(rooster[week]['beamer'])
        file.write('|')
        file.write(rooster[week]['leider_blauw'])
        file.write(' & ')
        file.write(rooster[week]['helper_blauw'])
        file.write('|')
        file.write(rooster[week]['leider_wit'])
        file.write(' & ')
        file.write(rooster[week]['helper_wit'])
        file.write('|')
        file.write(rooster[week]['leider_rood'])
        file.write('|')
        file.write(rooster[week]['koffie'])
        file.write('|')
        if 'missendteamlid' in rooster[week]: 
            file.write(rooster[week]['missendteamlid'])
            file.write(' mist, ')
        if 'mettegenzin' in rooster[week]: 
            file.write(rooster[week]['mettegenzin'])
            file.write(' liever niet, ')
        if 'nietvoorkeurpaar_blauw' in rooster[week]: 
            file.write('afwijkend paar blauw, ')
        file.write(' |\n')
    file.close()

page = get_page()
beschikbaarheid = parse_table(page)
rooster = get_results(beschikbaarheid)
write_markup('rooster.txt', rooster)
