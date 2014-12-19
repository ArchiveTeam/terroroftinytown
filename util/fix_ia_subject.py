'''Script to add subject tags with the shortener project ids.'''

import internetarchive

ACCESS_KEY = 'TODO'
SECRET_KEY = 'TODO'


def main():
    search = internetarchive.search.Search('urlteam terroroftinytown -collection:test_collection')

    for result in search:
        print(result)

        item = internetarchive.get_item(result['identifier'])

        if not item.metadata['subject'] == 'urlteam;terroroftinytown':
            continue

        subjects = ['urlteam', 'terroroftinytown', 'archiveteam']

        for file_obj in item.iter_files():
            if file_obj.name.endswith('.zip'):
                shortener_id = file_obj.name.split('.', 1)[0]
                subjects.append(shortener_id)

        new_subject = ';'.join(subjects)

        print(new_subject)

        item.modify_metadata(
            {'subject': new_subject},
            access_key=ACCESS_KEY, secret_key=SECRET_KEY
        )


if __name__ == '__main__':
    main()
