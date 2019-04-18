
from terroroftinytown.services.base import BaseService
from terroroftinytown.services.status import URLStatus
import re

class GooglService(BaseService):
	def process_response(self, response):
		status_code = response.status_code

		if status_code in self.params['redirect_codes']:
			if self.ratelimited(response):
				return self.process_banned(response)
			return self.process_redirect(response)
		elif status_code in self.params['no_redirect_codes']:
			return self.process_no_redirect(response)
		elif status_code in self.params['unavailable_codes']:
			return self.process_unavailable(response)
		elif status_code in self.params['banned_codes']:
			return self.process_banned(response)
		else:
			return self.process_unknown_code(response)

	def ratelimited(self, response):
		if 'Location' not in response.headers:
			return False
		result_url = response.headers['Location']
		response.content  # read the response to allow connection reuse
		return not not re.search('^https?://(?:www\.)?google\.com/sorry', result_url)
