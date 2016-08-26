#!/usr/bin/env python
domain = 'http://www.ichthusculemborg.nl/services'


def exists(availabilities, person, task, week):
    if task in availabilities:
        if person in availabilities[task]:
            return week in availabilities[task][person]
    return False


def show_help():
    print(sys.argv[0], ' [-h] [-f <from week>] [-t <till week>]')
    print('\t-f\tFrom week.')
    print('\t-h\tThis help.')
    print('\t-t\tTill week.')


if __name__ == "__main__":
    import sys
    import getopt
    import getpass
    from services import Services

    from_week = 40
    till_week = 52
    domain = "http://www.ichthusculemborg.nl/services"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:t:")
    except getopt.GetoptError:
        print("Incorrect arguments.")
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
        print("Till-week must be greater then from-week.")
        sys.exit(2)
    print('get password')
    password = getpass.getpass('Password for hans.kalle@telfort.nl: ')
    print('get persons')
    services = Services(domain, ('hans.kalle@telfort.nl', password))
    persons = services.get_persons()
    print(persons)
    print('get commitments')
    commitments = services.get_commitments()
    print(commitments)
    print('get availability')
    availabilities = services.get_availabilities()
    print(availabilities)
    for task in commitments:
        for person in commitments[task]:
            if person not in ["In_de_dienst", "Niemand"]:
                for week in range(from_week, till_week + 1):
                    if not exists(availabilities, task, person, week):
                        print(services.post_availability(persons[person]['uid'], person, task, week, "yes"))
