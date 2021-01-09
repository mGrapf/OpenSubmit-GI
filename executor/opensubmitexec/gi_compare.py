#!/usr/bin/env python
import re

def compare(output_example : str, output_submission : str, config : {}):
	
	# DEBUG_config_string
	debug_text = ""
	def dprint(text='', end='\n'):
		nonlocal debug_text
		debug_text += text + end

	
	# Remove whitespaces left and right
	output_example = output_example.strip()
	output_submission = output_submission.strip()
	
	# Everything in lower case? (Default)
	if config['compare_case_sensitive']:
		dprint('- compare_case_sensitive')
	else:
		output_example = output_example.lower()
		output_submission = output_submission.lower()
		
	
	if config['remove_whitespaces']:
		dprint('- remove_whitespaces')
	if config['group_lines']:
		dprint('- group_lines')
	if config['group_words']:
		dprint('- group_words')
	if config['skip_first_lines']:
		dprint('- skip_first_lines')
	if config['skip_lines']:
		dprint('- skip_lines')
	if config['skip_words']:
		dprint('- skip_words')
	if config['skip_characters']:
		dprint('- skip_characters')
	if config['random_order_lines']:
		dprint('- random_order_lines')
	if config['random_order_words']:
		dprint('- random_order_words')
	if config['random_order_characters']:
		dprint('- random_order_characters')

	# Replace some strings?
	replace_example = output_example
	replace_submission = output_submission
	for key, value in config.items():
		if 'replace' in key and value:
			if not config['compare_case_sensitive']:
				value = value.lower()
			value = re.split('" *-> *"',value[1:-1])
			
			replace_example = output_example.replace(value[0],value[1])
			replace_submission = output_submission.replace(value[0],value[1])
			dprint('- '+key+': "'+value[0]+'" -> "'+value[1]+'"')
	output_example = replace_example
	output_submission = replace_submission
	
	# Compare only numbers? (optional)
	if config['compare_only_numbers']:
		replace_example = re.sub('[^\s0-9]+','',output_example)
		replace_submission = re.sub('[^\s0-9]+','',output_submission)
		if replace_example:
			output_example = replace_example
			output_submission = replace_submission
			dprint('- compare_only_numbers')
		else:
			dprint('- compare_only_numbers: error (string would be empty)')

	if debug_text:
		debug_text = '### Konfiguration: ###\n'+debug_text

	"""
	print("Debug")
	print('### Beispieltext: ###')
	for e in output_example.split('\n'):
		print('|'+e+'|')
	print()
	print('### Zu vergleichender Text ###')
	for e in output_submission.split('\n'):
		print('|'+e+'|')
	print()
	"""
	
	if output_example == "":
		raise Exception('The string "output_example" is empty')
	dprint()
	
	# group?
	if config['skip_first_lines'] or config['skip_lines'] or config['random_order_lines']:
		config['group_lines'] = True
	if config['skip_words'] or config['random_order_words']:
		config['group_words'] = True

	
	
	# Split text into lines
	if config['group_lines']:
		output_example = output_example.split('\n')
		output_submission = output_submission.split('\n')
	else:
		output_example = [output_example]
		output_submission = [output_submission]
	
	# Split lines into words
	for line in range(len(output_example)):
		if config['group_words']:
			output_example[line] = output_example[line].split()
		else:
			output_example[line] = [output_example[line]]
	for line in range(len(output_submission)):
		if config['group_words']:
			output_submission[line] = output_submission[line].split()
		else:
			output_submission[line] = [output_submission[line]]
	
	# Split lines into characters
	for line in range(len(output_example)):
		for word in range(len(output_example[line])):
			if config['skip_characters'] or config['random_order_characters']:
				output_example[line][word] = list(re.sub('\s','',output_example[line][word]))
			elif config['remove_whitespaces']:
				output_example[line][word] = [re.sub('\s','',output_example[line][word])]
			else:
				output_example[line][word] = [output_example[line][word]]
	for line in range(len(output_submission)):
		for word in range(len(output_submission[line])):
			if config['skip_characters'] or config['random_order_characters']:
				output_submission[line][word] = list(re.sub('\s','',output_submission[line][word]))
			elif config['remove_whitespaces']:
				output_submission[line][word] = [re.sub('\s','',output_submission[line][word])]
			else:
				output_submission[line][word] = [output_submission[line][word]]
	
	# remove empty lines
	tmp = []
	for e in output_example:
		if e != [[]]:
			tmp.append(e)
	output_example = tmp
	tmp = []
	for s in output_submission:
		if s != [[]]:
			tmp.append(s)
	output_submission = tmp

	
	# Compare characters individually
	def compare_characters(output_example,output_submission,config):
		output_example = output_example.copy()
		output_submission = output_submission.copy()
		i = 0
		for e in output_example:
			try:
				if config['random_order_characters']:
					i = 0
				while(e != output_submission[i]):
					i += 1
				output_submission.pop(i)
			except Exception as e:
				return False
		if output_submission and not config['skip_characters']:
			return False
		return True
	
	# Compare words individually
	def compare_words(output_example,output_submission,config):
		output_example = output_example.copy()
		output_submission = output_submission.copy()
		i = 0
		for e in output_example:
			try:
				if config['random_order_words']:
					i = 0;
				while compare_characters(e,output_submission[i],config) == False:
					i += 1
				output_submission.pop(i)
			except Exception as e:
				return False
		if output_submission and not config['skip_words']:
			return False
		return True
	
	# Compare lines individually
	def compare_lines(output_example,output_submission,config):
		i = 0
		for e in output_example:
			try:
				if config['random_order_lines']:
					i = 0;
				while compare_words(e,output_submission[i],config) == False:
					i += 1
				output_submission.pop(i)
			except Exception as e:
				return False
		if output_submission and not config['skip_lines']:
			return False
		return True
	
	# skip first lines
	if config['skip_first_lines']:
		try:
			ready = False
			while not ready:
				for i in range(len(output_example)):
					if not ready and compare_words(output_example[i],output_submission[0],config):
						ready = True
				if not ready:
					output_submission.pop(0)
		except:
			return False, debug_text
	
	# Text output for demonstration
	dprint('### Debug: Beispieltext: ###')
	for line in output_example:
		dprint('|',end='')
		for word in line:
			dprint('[',end='')
			for letter in word:
				dprint('['+letter+']',end='')
			dprint(']  ',end='')
		dprint('|')
	dprint()
	dprint('### Debug: Submission Text: ###')
	for line in output_submission:
		dprint('|',end='')
		for word in line:
			dprint('[',end='')
			for letter in word:
				dprint('['+letter+']',end='')
			dprint(']  ',end='')
		dprint('|')

	result = compare_lines(output_example,output_submission,config)
	return result, debug_text


if __name__ == '__main__':
	config = {}
	config['compare_case_sensitive'] = False	# Default = False
	config['compare_only_numbers'] = False		# Default = False
	config['remove_whitespaces'] = True			# Default = False
	config['replace'] = '"Matrix enthalten." -> "Matrix enthalten"'

	config['group_lines'] = False				# Default = False
	config['group_words'] = False				# Default = False

	config['skip_first_lines'] = True			# Defaylt = False
	config['skip_lines'] = False				# Default = False

	config['skip_words'] = False				# Default = False
	config['skip_characters'] = False			# Default = False
	
	config['random_order_lines'] = True		# Default = False
	config['random_order_words'] = False		# Default = False
	config['random_order_characters'] = False	# Default = False

	output_example = '''puma | [3] [4] | rechts
katze ist NICHT in der Matrix enthalten.
fuchs | [8] [15] | runter
'''
	output_submission = '''Wort 1 eingeben: Wort 2 eingeben: Wort 3 eingeben: 

puma |[3] [4]| rechts
katze ist in der Matrix nicht enthalten.
fuchs |[8] [15]| runter
'''
	
	equal, debug_text = compare(output_example,output_submission,config)
	print(debug_text)
	
	print('End result:')
	if equal:
		print('The submitted text contains the example text!')
	else:
		print('According to the current configuration,\nthe submitted text is assessed as different.')

	




