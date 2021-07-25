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
from opensubmitexec.gi_test_cases import createTests
from .exceptions import *
logger = logging.getLogger('opensubmitexec')


def validate(job):
	logger.debug("start gi_validator")
	
	fname_example = job.cpp_example
	fname_main = job.cpp_main
	fname_config = job.cpp_config
	
	
	"""
	if len(job.validator_files) == 1:
		fname_example = job.validator_files[0]
		fname_main = None
	else:
		cpp_files = []
		for file in job.validator_files:
			if file.endswith(".cpp"):
				cpp_files.append(file)
		if len(cpp_files) > 2:
			job.send_fail_result("There are a problem with the cpp-validator ;(","Too many Validator CPP files were submitted.")
			return
		for file in cpp_files:
			with open (job.working_dir+file, "r",encoding="utf-8") as cpp:
				code = cpp.read()
				if "[CONFIG]" in code and ";EOF" in code:
					logger.debug("The cpp-configuration is in "+file)
					fname_main = file
					cpp_files.remove(file)
					fname_example = cpp_files[0]
					break
	"""

	""" Lese example """
	def read_file(fname: str) -> str:
		with open(job.working_dir+fname, 'r',encoding="utf-8", errors='ignore') as f:
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
	""" Konfigurationsfile """
	conf_file = example
	if fname_config == fname_main:
		conf_file = main
	
	
	""" Lese Konfiguration """
	def readConfig(cpp : str) -> dict:   
		default_config='''[CONFIG]
			# General Settings
				submission_filename = 
				forbid_loops = FALSE
				allow_libraries =
				
			# Settings for the test creation		
				hide_input = FALSE
				input_time = 0.01
				test_1 = 
				
			# Settings for output comparison:
				replace_text_1 = 
				compare_whitespaces = FALSE
				compare_case_insensitive = FALSE
				compare_only_numbers = FALSE
                compare_numbers = FALSE
                compare_letters = FALSE
				
				skip_first_lines = FALSE
				skip_lines = FALSE
				skip_words = FALSE
				skip_chars = FALSE
				
				random_line_order = FALSE
				random_word_order = FALSE
				random_char_order = FALSE
				
				compare_line_by_line = FALSE
				compare_word_by_word = FALSE
				'''
		config = ConfigParser()
		config.read_string(default_config)
		
		""" Konfiguration aus cpp lesen """
		pos1 = re.search("\[CONFIG\]",cpp)
		pos2 = re.search(";EOF",cpp)
		if pos1 and pos2:
			cpp = cpp[pos1.span()[1]:pos2.span()[0]]
			try:
				tmp_cpp = "[CONFIG]"
				for line in cpp.splitlines():
					line = re.sub("^[^A-Za-z#]+","",line)
					config.read_string("[CONFIG]\n"+line)
					tmp_cpp = tmp_cpp+line+'\n'
			except:
				raise Exception("Fehlerhafte Zeile in cpp-Konfiguration: "+line)
			try:
				config.read_string(tmp_cpp)
			except:
				raise Exception("Doppelter Eintrag in cpp-Konfiguration:\n"+tmp_cpp)
		else:
			logger.warning("Konnte keine Konfiguration finden!")
		""" Kontrolliere Konfiguration """
		for conf_name in config['CONFIG']:
			if conf_name not in default_config and not conf_name.startswith('test_') and not conf_name.startswith('replace_'):
				raise Exception("Ungueltiger Eintrag in cpp-Konfiguration: "+conf_name)
		
		""" Speichere alles in Dictionary """
		dconfig = dict(config.items('CONFIG'))
		dconfig['submission_filename'] = config.get('CONFIG', 'submission_filename')
		dconfig['forbid_loops'] = config.getboolean('CONFIG', 'forbid_loops')
		dconfig['allow_libraries'] = config.get('CONFIG', 'allow_libraries')
		dconfig['hide_input'] = config.getboolean('CONFIG', 'hide_input')
		dconfig['input_time'] = config.getfloat('CONFIG', 'input_time')
		dconfig['compare_case_insensitive'] = config.getboolean('CONFIG', 'compare_case_insensitive')
		dconfig['compare_only_numbers'] = config.getboolean('CONFIG', 'compare_only_numbers')
		dconfig['compare_numbers'] = config.getboolean('CONFIG', 'compare_numbers')
		dconfig['compare_letters'] = config.getboolean('CONFIG', 'compare_letters')
		dconfig['compare_whitespaces'] = config.getboolean('CONFIG', 'compare_whitespaces')
		dconfig['compare_line_by_line'] = config.getboolean('CONFIG', 'compare_line_by_line')
		dconfig['compare_word_by_word'] = config.getboolean('CONFIG', 'compare_word_by_word')
		dconfig['skip_first_lines'] = config.getboolean('CONFIG', 'skip_first_lines')
		dconfig['skip_lines'] = config.getboolean('CONFIG', 'skip_lines')
		dconfig['skip_words'] = config.getboolean('CONFIG', 'skip_words')
		dconfig['skip_chars'] = config.getboolean('CONFIG', 'skip_chars')
		dconfig['random_line_order'] = config.getboolean('CONFIG', 'random_line_order')
		dconfig['random_word_order'] = config.getboolean('CONFIG', 'random_word_order')
		dconfig['random_char_order'] = config.getboolean('CONFIG', 'random_char_order')
		return dconfig
	
	""" Konfiguration lesen """
	
	try:
		config = readConfig(conf_file)
	except Exception as e:
		logger.error(e)
		job.send_fail_result("Validatorfehler :(", str(e))
		return

		
		
		
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
	


	""" Kommentare entfernen """
	def remove_comments(data: str) -> str:
		data = re.sub("//.*\n", "\n", data)
		while re.search("/[*]",data) and re.search("[*]/",data):
			pos = re.search("/[*]",data).span()[0]
			pos2 = re.search("[*]/",data).span()[1]
			data = data[:pos] + data[pos2:]
		return data
	example = remove_comments(example)
	submission = remove_comments(submission)

	""" Kompiliere zunächst die Abgabe """
	logger.debug("::: Kompiliere zunaechst die Abgabe.")
	if not re.search("int(\n| )+main(\n| )*[(].*[)](\n| )*{",submission):
		logger.debug("::: main() existiert nicht. -> Füge main() hinzu.")
		with open(job.working_dir+fname_submission, 'w',encoding="utf-8") as f:
			f.write(submission + 'int main(){return 0;}')
	try:
		job.run_compiler(compiler=GPP, inputs=[fname_submission], output='submission')
	except Exception as e:
		if type(e) is WrongExitStatusException and "was not declared" in e.output: # Funktionen der main.cpp werden nicht in der submission.cpp gefunden
			function = e.output.splitlines()[2].strip()
			job.send_fail_result("Eine Funktion/Klasse wurde nicht definiert: "+function,'Output of '+e.instance.name+': '+e.output)
			return
		else:
			raise e
	logger.debug("::: 1. Kompilierung erfolgreich.")

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
	#if fname_main and re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',main):
	#	if re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',example):
	#		logger.debug("::: remove main() from example")
	#		example = remove_main(example)
	#	if re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',submission):
	#		logger.debug("::: remove main() from submission")
	#		submission = remove_main(submission)
	
	""" Rekursion """
	if config['forbid_loops']:
		submission_r = remove_main(submission)
		if re.search("for *[(].*;.*;.*[)]",submission_r) or re.search("while *[(].+[)]",submission_r):
			job.send_fail_result("Sie haben Schleifen verwendet! Diese Aufgabe soll rekursiv gelöst werden.", "Student used loops.")
			return
	
	""" ggf. main-Funktion umbenennen """
	if fname_main and re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',main):
		if re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',example):
			logger.debug("::: rename main() from example")
			example = re.sub("int(\n| )+main(\n| )*[(].*[)](\n| )*{","int main2(){",example)
		if re.search('int(\n| )+main(\n| )*[(].*[)](\n| )*{',submission):
			logger.debug("::: rename main() from submission")
			submission = re.sub("int(\n| )+main(\n| )*[(].*[)](\n| )*{","int main2(){",submission)

	""" Verbiete alle Bibliotheken, welche nicht im example vorkommen """
	i_example = re.findall("#\s*include\s+[<|\"]\w+[>|\"]",example)
	i_example = re.sub("#\s*include\s+[<|\"]|[>|\"]",'',', '.join(i_example))
	i_submission = re.findall("#\s*include\s+[<|\"]\w+[>|\"]",submission)
	for include in i_submission:
		include = re.sub("#\s*include\s+[<|\"]|[>|\"]",'',include)
		if include not in i_example and include not in config['allow_libraries']:
			if not i_example:
				i_example = "keine"
			job.send_fail_result("Das Einbinden der Bibliothek <"+include+"> ist in dieser Aufgabe nicht erlaubt!\nErlaubt sind: "+i_example)
			return

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
	""" remove from main """
	main = re.sub("(\A| |\n)# *include +<iostream>","",main)
	main = re.sub("(\n| )using +namespace +std*;","",main)

	
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
		try:
			job.run_compiler(compiler=GPP, inputs=[fname_main], output='submission')
		except Exception as e:
			if type(e) is WrongExitStatusException:				
				undefiniert = re.search('Warnung: undefinierter Verweis auf .+\n',e.output)
				if undefiniert:
					error = e.output[undefiniert.span()[0]+35:undefiniert.span()[1]]
					job.send_fail_result("Eine Funktion/Klasse wurde nicht gefunden: "+error,'Output of '+e.instance.name+': '+e.output)
					return
				else:
					job.send_fail_result("Fehler beim Kompilieren: "+e.output,e.output)
				return
			else:
				raise e

	""" create test-cases """
	def createOldTests(config : {}) -> [str]:
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
	try:
		testcases = createTests(config)
	except Exception as e:
		job.send_fail_result("Interner Validatorfehler: Testcases",str(e))
		return

	i = 1
	info_tests = "### Input:\n"
	for test in testcases:
		info_tests += "Test " + str(i) + ':\t' + test+'\t'
		
		if test == "$NOINPUT":
			exit_code_example, output_example = job.run_program('./example')
			exit_code_submission, output_submission = job.run_program('./submission')
		else:
			# Example ausführen
			running_example = job.spawn_program('./example', [test], echo=not config['hide_input'])
			running_submission = job.spawn_program('./submission', [test], echo= not config['hide_input'])
			if not config['hide_input']:
				for word in test.split():
					time.sleep(config['input_time'])
					running_example.sendline(word)
					running_submission.sendline(word)
			else:
				running_example.sendline(test)
				running_submission.sendline(test)
			time.sleep(1)
			exit_code_example, output_example = running_example.expect_end()
			exit_code_submission, output_submission = running_submission.expect_end()
			l = len(test)
			output_example = output_example[l+1:]
			output_submission = output_submission[l+1:]

		
		# Notizen in example suchen
		output_notes = []
		notes = ''
		while("<COMMENT>" in output_example) and ("</COMMENT>" in output_example):
			pos1 = output_example.find("<COMMENT>")
			pos2 = output_example.find("</COMMENT>")
			output_notes.append(output_example[pos1+9:pos2])
			output_example = output_example[:pos1]+output_example[pos2+10:]
		if output_notes:
			notes = "Hinweis:"
			for note in output_notes:
				notes = note+"\n"
		# Notizen in submission suchen
		while("<COMMENT>" in output_submission) and ("</COMMENT>" in output_submission):
			pos1 = output_submission.find("<COMMENT>")
			pos2 = output_submission.find("</COMMENT>")
			output_submission = output_submission[:pos1]+output_submission[pos2+10:]

		# Verstecketen Text in example ausblenden
		while("<HIDDEN>" in output_example) and ("</HIDDEN>" in output_example):
			pos1 = output_example.find("<HIDDEN>")
			pos2 = output_example.find("</HIDDEN>")
			output_example = output_example[:pos1]+output_example[pos2+9:]
		# Verstecketen Text in submission ausblenden
		while("<HIDDEN>" in output_submission) and ("</HIDDEN>" in output_submission):
			pos1 = output_submission.find("<HIDDEN>")
			pos2 = output_submission.find("</HIDDEN>")
			output_submission = output_submission[:pos1]+output_submission[pos2+9:]
		
		# DEBUG Output
		
		if job._online == False:
			logger.debug('Submission Input: '+test)
			if notes:
				logger.debug('Notes:\n'+notes)
			logger.debug('Submission Output:\n\n'+output_submission+'\n')
		
		# Leeren Anfang und Ende entfernen
		output_example = output_example.strip()
		output_submission = output_submission.strip()
		while output_example and output_example[0] == '\n':
			output_example = output_example[1:].strip()
		while output_submission and output_submission[0] == '\n':
			output_submission = output_submission[1:].strip()
		while output_example and output_example[-1] == '\n':
			output_example = output_example[:-1].strip()
		while output_submission and output_submission[-1] == '\n':
			output_submission = output_submission[:-1].strip()


		# Exit-Codes vergleichen  
		if exit_code_submission == None:
			job.send_fail_result(notes+"\n### Ihre Ausgabe: ###\n"+output_submission+"\n\nIhr Programm scheint abzustürzen.\n(evtl. Speicherzugriffsfehler?)")
			return
		# Exit-Codes vergleichen  
		if exit_code_example != exit_code_submission:
			job.send_fail_result("Ihr Programm wurde nicht ordentlich beendet :/\nErwarteter Exit-Code: {0}\nIhr Exit-Code: {1}\n\n### Erwartete Ausgabe: ###\n{2}\n\n\n### Ihre Ausgabe: ###\n{3}".format(exit_code_example,exit_code_submission,output_example,output_submission),"Wrong exit-code")
			return	

		# Existenz der Ausgabe prüfen
		if re.sub('\s','',output_example) == "":
			job.send_fail_result("Validatorfehler :(", "Ihr cpp-example erzeugt keine Ausgabe!")
			return
		if re.sub('\s','',output_submission) == "":
			job.send_fail_result("Ihr Programm erzeugt keine Ausgabe!")
			return

		# DEBUG
		#print("### Submission Output: ###\n"+output_submission+"\n")

		# Output vergleichen
		ok, debug_text = compare(output_example,output_submission,config)
		
		info_student = notes+"\n### Erwartete Ausgabe: ###\n"+output_example+"\n\n### Ihre Ausgabe: ###\n"+output_submission+"\n\nLeider enthält Ihr Code nicht die erwartete Ausgabe :/"
		
		if not ok:
			info_tests += '<fail>\n'
			info_tutor = info_tests +'\n'+ debug_text
			#print("\n\nSende an Tutor:\n"+info_tutor)
			#print("\n\nSende an Studenten:\n"+info_student)
			job.send_fail_result(info_student,info_tutor)
			return
		info_tests += '<pass>\n'
		info_tutor = info_tests +'\n### Last Output:\n'+ output_example
		i += 1
	# Alle Tests erfolgreich
	job.send_pass_result('All tests passed. Awesome!', info_tutor)
	
