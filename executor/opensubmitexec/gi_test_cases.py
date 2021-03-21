#!/usr/bin/env python
import re
from random import uniform, choice
from os import remove, urandom, path

def createTests(config : {}) -> [str]:
	testcases = [] # create a test-list
	for key, value in config.items():
		if key.startswith('test'):
			
			# Dublicate Commands
			to_duplicate = re.findall("[$](?:[0-9]+[*])[^$)]*\)",value)
			for command in to_duplicate:
				number = re.match('[$][0-9]+[*]',command)
				new_command = ''
				for replace in range(int(number.group()[1:-1])):
					new_command = new_command+'$'+command[number.span()[1]:]+' '
				value = value.replace(command,new_command)
			
			# $RANDOM
			commands = re.findall("[$]RANDOM\( *[+\-]?[0-9]+(?:\.[0-9]+)? *, *[+\-]?[0-9]+(?:\.[0-9]+)? *\)",value)
			for command in commands:

				# Zufallszahl erzeugen
				numbers = re.findall('[+\-]?[0-9]+(?:\.[0-9]+)?',command)
				r = uniform(float(numbers[0]),float(numbers[1]))
				
				# Anzahl Nachkommastellen
				comma = 0
				for n in re.findall('\.[0-9]+',command):
					if len(n) > comma:
						comma = len(n)-1
				
				# Runden
				r = round(r,comma)
				if (r % 1.0 == 0):
					r = int(r)
				value = value.replace(command,str(r),1)
			
			# $CHOICE
			commands = re.findall("\$CHOICE\([^)]+\)",value)
			for command in commands:
				choices = re.sub('\$CHOICE|[()\"\']','',command).split(',')
				value = value.replace(command,choice(choices))
			
			# Failtest $
			fail = re.search("\$",value)
			if fail:
				raise Exception("Zeichen '$' konnte in cpp-Konfiguration nicht aufgeloest werden: {0} = {1}".format(key,fail.string))
			if value:
				testcases.append(value.strip())
	if not testcases:
		testcases.append('$NOINPUT')
	return testcases



if __name__ == '__main__':
	config = {}
	config['test_a'] = "$1*RANDOM(2, 1.0000 ) $3*RANDOM( 1.0 ,0 ) $1*RANDOM(33,3) fe"
	config['test_1'] = "eger 8 ewfw 23 2 3 RANDOM"
	config['test_2'] = "$1*RANDOM(-5, 5 ) "
	config['test_3'] = "$RANDOM(1, 5 ) "
	config['test_4'] = "$1*RANDOM(-5, 5 ) $RANDOM(34,2) $CHOICE(aa,b,ccc) $CHOICE(\"dd\",'eeee')"


	tests = createTests(config)
	for test in tests:
		print(test)

