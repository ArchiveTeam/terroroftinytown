# encoding=utf-8
from terroroftinytown.client.errors import PleaseRetry
from terroroftinytown.services import registry

class Scraper(object):
    '''URL shortner scraper.

    Args:
        shortener_params (dict): The mapping has the keys:

            * url_template (str)
            * alphabet (str)
            * redirect_codes (list)
            * no_redirect_codes (list)
            * unavailable_codes (list)
            * banned_codes (list)

        todo_list (list): A list of integers.

    '''

    retry_count = 10

    def __init__(self, shortener_params, todo_list):
        self.params = shortener_params
        self.todo_list = todo_list
        self.results = {}
        self.service = self.get_service()(self.params)

    def run(self):
        while self.todo_list:
            for try_count in range(self.retry_count):
                if try_count > 0:
                    print('Attempt %d' % (try_count + 1))
                
                try:
                    result = self.service.scrape_one(self.todo_list.pop())

                    if result:
                        self.results[result['shortcode']] = result
                except PleaseRetry:
                    pass
                else:
                    break
                finally:
                    self.service.wait()

        return self.results

    def get_service(self):
        if self.params['name'] in registry:
            return registry[self.params['name']]
        else:
            return registry['_default']
