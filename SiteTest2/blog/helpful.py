#coding:utf-8
import re
def remove_html(text):
	bad_symbols = {r'<':'&lt;', r'>':'&gt;'}
	for key in bad_symbols.keys():
		ret_text = re.sub(key, bad_symbols[key], text)
	return ret_text

def do_p(text):
	ret_text = re.sub('\n', '<br>', text)
	return ret_text