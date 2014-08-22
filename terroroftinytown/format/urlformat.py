# encoding=utf-8
'''Validation and formatting of shortcode and URL data.'''

import string

def quote(text, safe=string.digits):
	'''URL Encoding similar to urllib's, but with more strict safe characters'''
	if not isinstance(text, (bytes, bytearray)):
		raise TypeError('quote() input must be bytes or bytesarray')

	safe = safe.encode('ascii', 'ignore')

	return ''.join(['%{:02X}'.format(b) if b not in safe else chr(b) for b in text])