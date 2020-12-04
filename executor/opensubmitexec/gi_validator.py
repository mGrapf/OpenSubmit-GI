from opensubmitexec.compiler import GPP
import opensubmitexec.exceptions
from os import remove, urandom, path
import re
from random import uniform, seed
from configparser import ConfigParser
import logging
import time
import sys
from opensubmitexec.gi_compare import compare
logger = logging.getLogger('opensubmitexec')


def validate(job):
	fname_example = job.validator_files[0]
	if len(job.validator_files) == 2:
		fname_main = job.validator_files[1]
	else:
		fname_main = None
	
	""" Lese example """
	def read_file(fname: str) -> str:
		with open(job.working_dir+fname, 'r',encoding="utf-8") as f:
			data = f.read()
		return data
	SECURITY_CODE = job._config.get("Server", "secret")
	example = '//'+SECURITY_CODE+'\n'+read_file(fname_example)
	""" Lese ggf. validator_main.cpp """
	if fname_main:
		main = read_file(fname_main)
		with open(job.working_dir+fname_main, 'w',encoding="utf-8") as f:
			f.write('//'+SECURITY_CODE+'\n'+main)
	else:
		fname_main = None
		main = example
		logger.debug("::: Keine validator_main.cpp gefunden.")
	
	""" Lese Konfiguration """
	def readConfig(data : str) -> dict:    
		config = ConfigParser()
		config.read_string('''
		[CONFIG]
		SUBMISSION_FILENAME = 
		FORBID_LOOPS = FALSE
		ALLOW_LIBRARIES =
		SEPARATOR = '\a'
		EXTRA_COMPILATION = FALSE
		INPUT_TIME = 0.1
		ECHO_INPUT = TRUE
		
		TEST_CASE_0 = 
		TEST_CASE_N =
		N_TEST_CASES = 1
		
		RANDOM_MIN = 1
		RANDOM_MAX = 100
		RANDOM_FLOAT = 0
		
		
		COMPARE_WHITE_SPACES = FALSE
		COMPARE_NEWLINE = FALSE
		COMPARE_ONLY_LETTERS = FALSE
		COMPARE_ONLY_PARTS = FALSE
		COMPARE_LINE_BY_LINE = FALSE
		
		
		
		COMPARISON_MODE = 0
		COMPARE_SKIP = 0
		COMPARE_SKIP_FIRST = TRUE
		COMPARE_ANY_ORDER = FALSE
		COMPARE_SPACES = FALSE
		
		
		COMPARE_CASE_SENSITIVE = FALSE
		COMPARE_ONLY_NUMBERS = FALSE
		
		''')
		try:
			pos1 = re.search("\[CONFIG\]",data).span()[0]
			pos2 = re.search(";EOF",data).span()[0] 
			ini = re.sub("//",'',data[pos1:pos2])
			config.read_string(ini)
		except:
			logger.debug("::: Kann keine Konfiguration lesen.")
		""" Speichere alles in Dictionary """
		dconfig = dict(config.items('CONFIG'))
		dconfig['n_test_cases'] = config.getint('CONFIG', 'n_test_cases')
		dconfig['random_min'] = config.getfloat('CONFIG', 'random_min')
		dconfig['random_max'] = config.getfloat('CONFIG', 'random_max')
		dconfig['random_float'] = config.getint('CONFIG', 'random_float')
		dconfig['recursion'] = config.getboolean('CONFIG', 'forbid_loops')
		dconfig['echo_input'] = config.getboolean('CONFIG', 'echo_input')
		dconfig['allow_libraries'] = config.get('CONFIG', 'allow_libraries')
		dconfig['input_time'] = config.getfloat('CONFIG', 'input_time')
		dconfig['extra_compilation'] = config.getboolean('CONFIG', 'extra_compilation')
		dconfig['compare_case_sensitive'] = config.getboolean('CONFIG', 'compare_case_sensitive')
		dconfig['compare_white_space'] = config.getboolean('CONFIG', 'compare_white_spaces')
		dconfig['compare_newline'] = config.getboolean('CONFIG', 'compare_newline')
		dconfig['compare_only_numbers'] = config.getboolean('CONFIG', 'compare_only_numbers')
		dconfig['compare_only_letters'] = config.getboolean('CONFIG', 'compare_only_letters')
		dconfig['compare_only_parts'] = config.getboolean('CONFIG', 'compare_only_parts')
		dconfig['compare_line_by_line'] = config.getboolean('CONFIG', 'compare_line_by_line')
		
		dconfig['comparison_mode'] = config.getint('CONFIG', 'comparison_mode')
		dconfig['compare_skip'] = config.getint('CONFIG', 'compare_skip')
		dconfig['compare_skip_first'] = config.getboolean('CONFIG', 'compare_skip_first')
		dconfig['compare_any_order'] = config.getboolean('CONFIG', 'compare_any_order')
		dconfig['compare_spaces'] = config.getboolean('CONFIG', 'compare_spaces')
		return dconfig
	config = readConfig(main)
	
	""" Submission einlesen """
	if config['submission_filename']:
		fname_submission = config['submission_file']
		if fname_submission not in job.student_files:
			job.send_fail_result("Ihre Abgabe muss den Dateinamen \"{0}\" besitzen!".format(fname_submission), "Submission nicht gefunden")
			return
	else:
		if len(job.student_files) != 1:
			logger.debug(job.student_files)
			job.send_fail_result("Bitte genau eine cpp-Datei abgeben!", "Ungültige Dateianzahl")
			return
		fname_submission = job.student_files[0]
	submission = read_file(fname_submission)
	
	""" Kompiliere zunächst die Abgabe """
	logger.debug("::: Kompiliere zunaechst die Abgabe.")
	if not re.search("int(\n| )+main(\n| )*[(].*[)](\n| )*{",submission):
		logger.debug("::: main() existiert nicht. -> Füge main() hinzu.")
		with open(job.working_dir+fname_submission, 'w',encoding="utf-8") as f:
			f.write(submission + 'int main(){return 0;}')
	job.run_compiler(compiler=GPP, inputs=[fname_submission], output='submission')
	logger.debug("::: 1. Kompilierung erfolgreich.")

	""" Kommentare entfernen """
	def remove_comments(data: str) -> str:
		data = re.sub("//.*\n", "\n", data)
		while re.search("/[*]",data):
			pos = re.search("/[*]",data).span()[0]
			pos2 = re.search("[*]/",data).span()[1]
			data = data[:pos] + data[pos2:]
		return data
	example = remove_comments(example)
	submission = remove_comments(submission)

	""" ggf. main-Funktion entfernen """
	def remove_main(data: str) -> str:
		pos = re.search("int(\n| )+main(\n| )*[(].*[)](\n| )*{",data)
		if pos:
			pos = pos.span()
			s1 = data[:pos[0]]
			s2 = data[pos[1]:]
			i = 0
			n = 1
			while(n):
				if s2[i] == '{':
					n += 1
				elif s2[i] == '}':
					n -= 1
				i+=1
			data = s1 + s2[i:]
		return data
	if fname_main and re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',main):
		if re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',example):
			logger.debug("::: remove main() from example")
			example = remove_main(example)
		if re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',submission):
			logger.debug("::: remove main() from submission")
			submission = remove_main(submission)
	
	
	""" Rekursion """
	if config['recursion']:
		if re.search("for *[(].*;.*;.*[)]",submission) or re.search("while *[(].+[)]",submission):
			job.send_fail_result("Du hast Schleifen verwendet!", "Student used loops.")

	""" iostream vorbereiten """
	def prepare_iostream(data: str) -> str:
		""" include <iostream> """
		if not re.search("(\A| |\n)# *include +<iostream>",data):
			data = "#include <iostream>\n" + data
		""" using namespace std; """
		if not re.search("(\n| )using +namespace +std*;",data):
			data = "using namespace std;\n" + data
		return data
	example = prepare_iostream(example)
	submission = prepare_iostream(submission)
	
	
	""" Verbiete alle Bibliotheken, welche nicht im example vorkommen """
	i_example = re.findall("#\s*include\s+[<|\"]\w+[>|\"]",example)
	i_example = re.sub("#\s*include\s+[<|\"]|[>|\"]",'',', '.join(i_example))
	i_submission = re.findall("#\s*include\s+[<|\"]\w+[>|\"]",submission)
	for include in i_submission:
		include = re.sub("#\s*include\s+[<|\"]|[>|\"]",'',include)
		if include not in i_example and include not in config['allow_libraries']:
			job.send_fail_result("Das Einbinden der Bibliothek <"+include+"> ist in dieser Aufgabe nicht erlaubt!\nErlaubt: "+i_example)
			return
	
	""" Schreibe änderungen in Datei """
	def prepare_write(fname: str, data: str):
		with open(job.working_dir+fname, 'w',encoding="utf-8") as f:
			f.write(data)
	prepare_write(fname_example,example)
	prepare_write(fname_submission,submission)


	""" Kompiliere """
	if not fname_main:
		""" 1. example; 2. submission """
		job.run_compiler(compiler=GPP, inputs=[fname_example], output='example')
		job.run_compiler(compiler=GPP, inputs=[fname_submission], output='submission')
	else:
		""" 1. main + example; 2. main + submission """
		job.run_compiler(compiler=GPP, inputs=[fname_main], output='example')
		main = main.replace(fname_example,fname_submission)
		with open(job.working_dir+fname_main, 'w',encoding="utf-8") as f:
			f.write(main)
		job.run_compiler(compiler=GPP, inputs=[fname_main], output='submission')
	
	""" create test-cases """
	def createTests(config : {}) -> [str]:
		seed(urandom(100))
		def insertRandom(case : str, tests : []) -> [str]: # Replace $RANDOM with random numbers
			if not case:
				return tests
			def createRandom(n : int, s = '') -> str: # Generate a random number n times
				for r in range(0,n):
					random = uniform(config['random_min'],config['random_max'])
					s+=str(round(random,config['random_float']))+' '				
				if config['random_float'] == 0:
					s=s.replace('.0','')
				return s[:-1]
			if re.search("\$[^\d][\*]RANDOM", case):
				logger.error("::: The configuration may be incorrect: Please check $RANDOM!")
				job.send_fail_result("Der Validator ist fehlerhaft konfiguriert!","Validator fehlerhaft konfiguriert: $RANDOM wurde falsch geschrieben!")
				quit(0)
			for found in re.findall("\$\d+\*RANDOM", case):
				case = case.replace(found,createRandom(int(found[1:-7])),1)
			for found in re.findall('\$RANDOM',case):
				case = case.replace(found,createRandom(1),1)
			return tests.append(case)
		testcases = [] # create a test-list
		for key, value in config.items(): # read test-cases in config
			if 'test_case_' in key and key != 'test_case_n':
				insertRandom(value,testcases)
		if config['test_case_n']: # finally read test-case-n in config
			for n in range(0,config['n_test_cases']):
				insertRandom(config['test_case_n'],testcases)
		default = False
		if testcases == []: # if no tests defined -> test with random numbers
			default = True
			insertRandom("$NOINPUT",testcases)
		return testcases, default
	
	

	# Fuehre das Programm mehrmals mit entsprechenden cases aus
	testcases, defaulttest = createTests(config)	
	
	
		
	
	for test in testcases:
		
		if test == "$NOINPUT":
			exit_code_example, output_example = job.run_program('./example')
			exit_code_submission, output_submission = job.run_program('./submission')
		else:
			# Programme ausführen
			running_example = job.spawn_program('./example', [test], echo=config['echo_input'])
			running_submission = job.spawn_program('./submission', [test], echo=config['echo_input'])
			# Input senden
			for word in test.split():
				time.sleep(config['input_time'])
				running_example.sendline(word)
				running_submission.sendline(word)
			# Ausgabe der Programme lesen
			exit_code_example, output_example = running_example.expect_end()
			exit_code_submission, output_submission = running_submission.expect_end()
			l = len(test)
			output_example = output_example[l+1:]
			output_submission = output_submission[l+1:]
		
		
		# Existenz der Ausgabe prüfen
		if re.sub('\s','',output_example) == "":
			job.send_fail_result("Validatorfehler: Der Test erzeugt keine Ausgabe!", "Der Test erzeugt keine Ausgabe!")
			return
		if re.sub('\s','',output_submission) == "":
			job.send_fail_result("Das Programm erzeugt keine Ausgabe!")
			return
		
		# Exit-Codes vergleichen  
		if exit_code_example != exit_code_submission:
			job.send_fail_result("Dein Programm wurde nicht ordentlich beendet :/\nErwarteter Exit-Code: {0}\nDein Exit-Code: {1}\n\n### Erwartete Ausgabe: ###\n{2}\n\n\n### Deine Ausgabe: ###\n{3}".format(exit_code_example,exit_code_submission,output_example,output_submission),"Wrong exit-code")
			return	
		
		
		# Notizen suchen
		output_notes = []
		while("<COMMENT>" in output_example) and ("</COMMENT>" in output_example):
			pos1 = output_example.find("<COMMENT>")
			pos2 = output_example.find("</COMMENT>")
			output_notes.append(output_example[pos1+9:pos2])
			output_example = output_example[:pos1]+output_example[pos2+10:]
		# Verstecketen Text ausblenden
		while("<HIDDEN>" in output_example) and ("</HIDDEN>" in output_example):
			pos1 = output_example.find("<HIDDEN>")
			pos2 = output_example.find("</HIDDEN>")
			output_example = output_example[:pos1]+output_example[pos2+9:]
		
		# Output vergleichen
		original_example = output_example
		original_submission = output_submission
		ok,text = compare(output_example,output_submission,config)
		if not ok:
			if test == "$NOINPUT" or config['echo_input'] == True:
				job.send_fail_result("Leider erzeugt dein Code eine andere Ausgabe :/\n\n### Erwartete Ausgabe: ###\n{0}\n\n\n### Deine Ausgabe: ###\n{1}".format(output_example, output_submission), "wrong output")
			else:
				job.send_fail_result("Leider erzeugt dein Code eine andere Ausgabe :/\n\n### Eingabe: "+test+" ###\n\n### Erwartete Ausgabe: ###\n{0}\n\n\n### Deine Ausgabe: ###\n{1}".format(original_example, original_submission), "wrong output")
			print("##########################################")
			print(text)
			print("##########################################")
			return

	
		
		
	""" Tests waren erfolgreich. Kompiliere optional erneut """
	hinweis = ''
	if config['extra_compilation']:
		try:
			job.run_compiler(compiler=['g++','-pthread','-Wall','-Werror','-o','{output}', '{inputs}'], inputs=[fname_submission], output='submission')
		except Exception as e:
			hinweis = "\n\nBut the code isn't perfect yet!\n\Try: 'g++ -Wall "+fname_submission+'\''
	
	# Alle Tests erfolgreich
	print("Alle Tests erfolgreich!")
	job.send_pass_result('All tests passed. Awesome!'+hinweis, "All tests passed.")
	
