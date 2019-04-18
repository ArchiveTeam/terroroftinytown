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
		if sys.version_info[0] == 2 and isinstance(result_url, terroroftinytown.six.binary_type):
			# Headers are treated as latin-1
			# This is needed so that unit tests don't need to
			# do implicit unicode conversion. Ick!
			result_url = result_url.decode('latin-1')
		response.content  # read the response to allow connection reuse
		return not not re.search('^https?://(?:www\.)?google\.com/sorry', result_url)

	def process_redirect(self, response):
		if 'Location' in response.headers:
			result_url = response.headers['Location']

			if sys.version_info[0] == 2 and isinstance(result_url, terroroftinytown.six.binary_type):
				# Headers are treated as latin-1
				# This is needed so that unit tests don't need to
				# do implicit unicode conversion. Ick!
				result_url = result_url.decode('latin-1')

			response.content  # read the response to allow connection reuse
			return self.check_anti_regex(response, result_url, None)
		elif self.params.get('body_regex'):
			return self.process_redirect_body(response)
		elif self.tolerate_missing_location_header:
			response.content  # read the response to allow connection reuse
			return self.process_no_redirect(response)
		else:
			response.content  # read the response to allow connection reuse

			raise UnexpectedNoResult(
				'Unexpectedly did not get a redirect result for {0}'
				.format(repr(response.url))
			)
