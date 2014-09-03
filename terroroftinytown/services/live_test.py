'''Test live services.'''
import glob
import nose.tools
import os.path

from terroroftinytown import services
from terroroftinytown.services.status import URLStatus
from terroroftinytown.tracker.bootstrap import Bootstrap
from terroroftinytown.tracker.model import Project


def run():
    bootstrap = Bootstrap()
    bootstrap.start()

    filenames = get_definition_filenames()
    for filename in filenames:
        service_name = os.path.split(filename)[-1].replace('.txt', '')
        project = Project.get_plain(service_name)
        params = project.to_dict()
        service = services.registry[service_name](params)

        print('Brought up service', service)

        with open(filename) as def_file:
            for shortcode, expected_result in iterate_defintiion_file(def_file):
                service.current_shortcode = shortcode
                url = params['url_template'].format(shortcode=shortcode)

                print('Requesting %s', url)

                response = service.fetch_url(url)
                url_status, result_url = service.process_response(response)

                if url_status == URLStatus.ok:
                    nose.tools.assert_equal(expected_result, result_url)
                else:
                    nose.tools.assert_equal(expected_result, url_status)


def iterate_defintiion_file(file):
    for line in file:
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        shortcode, result = line.split('|', 1)

        yield (shortcode, result)


def get_definition_filenames():
    def_path = os.path.join(os.path.dirname(__file__), 'test-definitions')
    return glob.glob(def_path + '/*.txt')


if __name__ == '__main__':
    run()
