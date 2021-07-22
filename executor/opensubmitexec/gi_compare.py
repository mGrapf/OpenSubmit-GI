#!/usr/bin/env python
import re

def compare(output_example : str, output_submission : str, config : {}):
	# backwards compatibility:
	if config['compare_only_numbers']:
		config['compare_numbers'] = True
	
	# DEBUG_config_string
	debug_text = ""
	def dprint(text='', end='\n'):
		nonlocal debug_text
		debug_text += text + end	
	
	# Everything in lower case? (Default)
	if config['compare_case_insensitive']:
		dprint('- compare_case_insensitive')
		output_example = output_example.lower()
		output_submission = output_submission.lower()
		
	# group?
	if config['skip_first_lines'] or config['skip_lines'] or config['random_line_order']:
		config['compare_line_by_line'] = True
	if config['skip_words'] or config['random_word_order']:
		config['compare_word_by_word'] = True
	if config['skip_chars'] or config['random_char_order']:
		group_whitespaces = True
	else:
		group_whitespaces = False
	
	
	if config['compare_whitespaces']:
		dprint('- compare_whitespaces')
	if config['compare_line_by_line']:
		dprint('- compare_line_by_line')
	if config['compare_word_by_word']:
		dprint('- compare_word_by_word')
	if config['skip_first_lines']:
		dprint('- skip_first_lines')
	if config['skip_lines']:
		dprint('- skip_lines')
	if config['skip_words']:
		dprint('- skip_words')
	if config['skip_chars']:
		dprint('- skip_chars')
	if config['random_line_order']:
		dprint('- random_line_order')
	if config['random_word_order']:
		dprint('- random_word_order')
	if config['random_char_order']:
		dprint('- random_char_order')
		
	# Replace Tabs
	output_example = output_example.replace('\t','    ');
	output_submission = output_submission.replace('\t','    ');

	# Replace some strings?
	replace_example = output_example
	replace_submission = output_submission
	for key, value in config.items():
		if 'replace_' in key and value:
			if config['compare_case_insensitive']:
				value = value.lower()
			value = re.split('" *-> *"',value[1:-1])
			
			replace_example = output_example.replace(value[0],value[1])
			replace_submission = output_submission.replace(value[0],value[1])
			dprint('- '+key+': "'+value[0]+'" -> "'+value[1]+'"')
	output_example = replace_example
	output_submission = replace_submission
	
	# Compare only numbers or letters?
	if config['compare_numbers'] and config['compare_letters']:
		replace_example = re.sub('[^\s0-9A-Za-z]+','',output_example)
		replace_submission = re.sub('[^\s0-9A-Za-z]+','',output_submission)
		if replace_example != "":
			output_example = replace_example
			output_submission = replace_submission
			dprint('- compare_only_letters_and_numbers')
		else:
			dprint('- compare_only_letters_and_numbers: error (string would be empty)')
	elif config['compare_numbers']:
		replace_example = re.sub('[^\s0-9]+','',output_example)
		replace_submission = re.sub('[^\s0-9]+','',output_submission)
		if replace_example != "":
			output_example = replace_example
			output_submission = replace_submission
			dprint('- compare_only_numbers')
		else:
			dprint('- compare_numbers: error (string would be empty)')
	elif config['compare_letters']:
		replace_example = re.sub('[^\sA-Za-z]+','',output_example)
		replace_submission = re.sub('[^\sA-Za-z]+','',output_submission)
		if re.sub('\s','',output_example) != "":
			output_example = replace_example
			output_submission = replace_submission
			dprint('- compare_letters')
		else:
			dprint('- compare_letters: error (string would be empty)')

	# format config_string
	if debug_text:
		debug_text = '### Comparison configuration:\n'+debug_text+"\n"
	
	# example-string empty?
	if not re.sub('\s','',output_example):
		raise Exception('The example output is empty. Wrong configuration!')
	
	# Split text into lines
	if config['compare_line_by_line']:
		output_example = output_example.split('\n')
		output_submission = output_submission.split('\n')
	else:
		output_example = [output_example.replace('\n',' ')]
		output_submission = [output_submission.replace('\n',' ')]
	
	
	# Remove whitespaces left and right
	tmp = []
	for output in output_example:
		if output.strip():
			tmp.append(output.strip())
	output_example = tmp
	tmp = []
	for output in output_submission:
		if output.strip():
			tmp.append(output.strip())
	output_submission = tmp
	
	
	
	# Split lines into words
	for line in range(len(output_example)):
		if config['compare_word_by_word']:
			output_example[line] = output_example[line].split()
		else:
			output_example[line] = [output_example[line]]
	for line in range(len(output_submission)):
		if config['compare_word_by_word']:
			output_submission[line] = output_submission[line].split()
		else:
			output_submission[line] = [output_submission[line]]
	
	# Split lines into characters
	for line in range(len(output_example)):
		for word in range(len(output_example[line])):
			if not config['compare_whitespaces']:
				output_example[line][word] = re.sub('\s','',output_example[line][word])
			if group_whitespaces:
				#output_example[line][word] = list(re.sub('\s','',output_example[line][word]))
				output_example[line][word] = list(output_example[line][word])
			else:
				output_example[line][word] = [output_example[line][word]]
			"""
			if config['skip_characters'] or config['random_order_characters']:
				output_example[line][word] = list(re.sub('\s','',output_example[line][word]))
			elif config['remove_whitespaces']:
				output_example[line][word] = [re.sub('\s','',output_example[line][word])]
			else:
				output_example[line][word] = [output_example[line][word]]
			"""
	for line in range(len(output_submission)):
		for word in range(len(output_submission[line])):
			if not config['compare_whitespaces']:
				output_submission[line][word] = re.sub('\s','',output_submission[line][word])
			if group_whitespaces:
				#output_submission[line][word] = list(re.sub('\s','',output_submission[line][word]))
				output_submission[line][word] = list(output_submission[line][word])
			else:
				output_submission[line][word] = [output_submission[line][word]]
			"""
			if config['skip_characters'] or config['random_order_characters']:
				output_submission[line][word] = list(re.sub('\s','',output_submission[line][word]))
			elif config['remove_whitespaces']:
				output_submission[line][word] = [re.sub('\s','',output_submission[line][word])]
			else:
				output_submission[line][word] = [output_submission[line][word]]
			"""
	
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

	
	# Compare characters individually	-> [c][c]
	def compare_characters(output_example,output_submission,config):
		output_example = output_example.copy()
		output_submission = output_submission.copy()
		i = 0
		for e in output_example:
			try:
				if config['random_char_order']:
					i = 0
				while(e != output_submission[i]):
					i += 1
				output_submission.pop(i)
			except Exception as e:
				return False
		if output_submission and not config['skip_chars']:
			return False
		return True
	
	# Compare words individually	-> [ w[c][c] ]
	def compare_words(output_example,output_submission,config):
		output_example = output_example.copy()
		output_submission = output_submission.copy()
		i = 0
		for e in output_example:
			try:
				if config['random_word_order']:
					i = 0;
				while compare_characters(e,output_submission[i],config) == False:
					i += 1
				output_submission.pop(i)
			except Exception as e:
				return False
		if output_submission and not config['skip_words']:
			return False
		return True
	
	# Compare lines individually	-> [l [ w[c][c] ] ]
	def compare_lines(output_example,output_submission,config):
		i = 0
		for e in output_example:
			try:
				if config['random_line_order']:
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
	dprint('### Last Example Output:')
	for line in output_example:
		if not config['compare_word_by_word'] and not group_whitespaces:
			dprint('|',end='')
		for word in line:
			if config['compare_word_by_word'] and not group_whitespaces:
				dprint('[',end='')
			for letter in word:
				if group_whitespaces:
					dprint('['+letter+']',end='')
				else:
					dprint(letter,end='')
			if config['compare_word_by_word']:
				if not group_whitespaces:
					dprint('] ',end='')
				else:
					dprint(' ',end='')
		if not config['compare_word_by_word'] and not group_whitespaces:
			dprint('|')
		else:
			dprint('')
	dprint()
	dprint('### Last Submission Output:')
	for line in output_submission:
		if not config['compare_word_by_word'] and not group_whitespaces:
			dprint('|',end='')
		for word in line:
			if config['compare_word_by_word'] and not group_whitespaces:
				dprint('[',end='')
			for letter in word:
				if group_whitespaces:
					dprint('['+letter+']',end='')
				else:
					dprint(letter,end='')
			if config['compare_word_by_word']:
				if not group_whitespaces:
					dprint('] ',end='')
				else:
					dprint(' ',end='')
		if not config['compare_word_by_word'] and not group_whitespaces:
			dprint('|')
		else:
			dprint('')

	result = compare_lines(output_example,output_submission,config)
	return result, debug_text


if __name__ == '__main__':
	
############################ config ####################################
	config = {}
	config['compare_case_insensitive'] = False	# Default = False
	config['compare_numbers'] = False		# Default = False
	config['compare_letters'] = False		# Default = False
	config['replace_text_1'] = ''				# "Text" -> "neuer Text"

	
	config['compare_line_by_line'] = False		# Default = False
	config['compare_word_by_word'] = False		# Default = False
	config['compare_whitespaces'] = False		# Default = False

	config['skip_first_lines'] = False			# Defaylt = False
	config['skip_lines'] = False				# Default = False
	config['skip_words'] = False				# Default = False
	config['skip_chars'] = False				# Default = False
	
	config['random_line_order'] = False			# Default = False
	config['random_word_order'] = False			# Default = False
	config['random_char_order'] = False			# Default = False
	
	# backwards compatibility:
	config['compare_only_numbers'] = False
############################ /config ###################################
	

	output_example = '''hello world'''
	output_submission = '''hello     world'''
	
	equal, debug_text = compare(output_example,output_submission,config)
	print(debug_text)
	
	print('End result:')
	if equal:
		print('The submitted text contains the example text!')
	else:
		print('According to the current configuration,\nthe submitted text is assessed as different.')

	




