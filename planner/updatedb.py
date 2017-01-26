from getpass import getpass

from services import Services


def insert_missing_persons(services):
    persons = services.get_missing_persons()
    if persons:
        for person in persons:
            match = services.get_persons_matching(person['person'])
            if len(match) == 1:
                print(services.post_person(person['person'], match[0]['persoonid'], match[0]['email']))
            else:
                print(services.post_person(person['person'], '0', 'rooster@ichthusculemborg.nl'))
        print("Database is geupdate.")
    else:
        print("Database is al up-to-date.")


auth = ('hans.kalle@telfort.nl', getpass())
services = Services('http://www.ichthusculemborg.nl/services', auth)
insert_missing_persons(services)
