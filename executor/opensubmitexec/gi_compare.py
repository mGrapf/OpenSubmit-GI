#!/usr/bin/env python
import re

def compare(output_example : str, output_submission : str, config : {}, debug=False):
	
	# Text output for demonstration
	if debug:
		print('### Original example text: ###')
		for e in output_example.split('\n'):
			print('|'+e+'|')
		print()
		print('### Original submission text ###')
		for e in output_submission.split('\n'):
			print('|'+e+'|')
		print('\n\n')
		
	# Everything in lower case? (Default)
	if not config['compare_case_sensitive']:
		output_example = output_example.lower()
		output_submission = output_submission.lower()
	
	# Remove whitespaces left and right
	output_example = output_example.strip()
	output_submission = output_submission.strip()

	# Compare only numbers? (optional)
	if config['compare_only_numbers']:
		output_example = re.sub('[^\s0-9]+','',output_example)
		output_submission = re.sub('[^\s0-9]+','',output_submission)
	
	
	
	# Split text into lines
	if config['group_lines'] or config['skip_lines'] or config['random_order_lines']:
		output_example = output_example.split('\n')
		output_submission = output_submission.split('\n')
	else:
		output_example = [output_example]
		output_submission = [output_submission]
	
	# Split lines into words
	for line in range(len(output_example)):
		if config['group_words'] or config['skip_words'] or config['random_order_words']:
			output_example[line] = output_example[line].split()
		else:
			output_example[line] = [output_example[line]]
	for line in range(len(output_submission)):
		if config['group_words'] or config['skip_words'] or config['random_order_words']:
			output_submission[line] = output_submission[line].split()
		else:
			output_submission[line] = [output_submission[line]]
	
	# Split lines into characters
	for line in range(len(output_example)):
		for word in range(len(output_example[line])):
			if config['compare_whitespaces']==False or config['skip_characters'] or config['random_order_characters']:
				output_example[line][word] = list(re.sub('\s','',output_example[line][word]))
			else:
				output_example[line][word] = [output_example[line][word]]
	for line in range(len(output_submission)):
		for word in range(len(output_submission[line])):
			if config['compare_whitespaces']==False or config['skip_characters'] or config['random_order_characters']:
				output_submission[line][word] = list(re.sub('\s','',output_submission[line][word]))
			else:
				output_submission[line][word] = [output_submission[line][word]]

	# Text output for demonstration
	if debug:
		print('### Edited and listed example text: ###')
		for line in output_example:
			print('|',end='')
			for word in line:
				print('[',end='')
				for letter in word:
					print('[',end='')
					print(letter,end='')
					print(']',end='')
				print(']  ',end='')
			print('|')
		print()
		print('### Edited and listed submission text ###')
		for line in output_submission:
			print('|',end='')
			for word in line:
				print('[',end='')
				for letter in word:
					print('[',end='')
					print(letter,end='')
					print(']',end='')
				print(']  ',end='')
			print('|')
		print()
	
	
	
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
	
	return compare_lines(output_example,output_submission,config)


if __name__ == '__main__':
	config = {}
	config['compare_case_sensitive'] = False	# Default = False
	config['compare_only_numbers'] = False		# Default = False
	config['compare_whitespaces'] = False		# Default = False

	config['group_lines'] = False				# Default = False
	config['group_words'] = False				# Default = False
	
	config['skip_lines'] = True					# Default = False
	config['skip_words'] = False				# Default = False
	config['skip_characters'] = True			# Default = False
	
	config['random_order_lines'] = False		# Default = False
	config['random_order_words'] = False		# Default = False
	config['random_order_characters'] = False	# Default = False

	output_example = '''hello world'''
	output_submission = '''I'm there!
		Hello World!'''

	
	equal = compare(output_example,output_submission,config,debug=True)
	print('End result:')
	if equal:
		print('The submitted text contains the example text!')
	else:
		print('According to the current configuration,\nthe submitted text is assessed as different.')





