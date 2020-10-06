from opensubmitexec.compiler import GPP
import opensubmitexec.exceptions
from os import remove, urandom, path
import re
from random import uniform, seed
from configparser import ConfigParser
import logging
logger = logging.getLogger('opensubmitexec')

SECURITY_CODE = 'UmBYuRW70hy4q7VcTAzg'
# Sicherheits-Code: Wird dieser von Studenten eingelesen, wird die Ausgabe verweigert



def validate(job):
	fname_main = "validator_main.cpp"
	fname_example = "validator_example.cpp"
	
	""" Kontrolliere Dateianzahl Submission """
	if len(job.student_files) != 1:
		logger.debug(job.student_files)
		job.send_fail_result("Bitte genau eine cpp-Datei abgeben!", "Ungültige Dateianzahl")
		return
	fname_submission = job.student_files[0]
	
	""" Lese submission & example """
	def read_file(fname: str) -> str:
		with open(job.working_dir+fname, 'r',encoding="utf-8") as f:
			data = f.read()
		return data
	submission = read_file(fname_submission)
	example = '//'+SECURITY_CODE+'\n'+read_file(fname_example)
	""" Lese ggf. validator_main.cpp """
	if path.isfile(job.working_dir+fname_main):
		main = read_file(fname_main)
		with open(job.working_dir+fname_main, 'w',encoding="utf-8") as f:
			f.write('//'+SECURITY_CODE+'\n'+main)
	else:
		fname_main = None
		main = example
		logger.debug("::: Keine validator_main.cpp gefunden.")
	
	""" Lese Konfiguration """
	def readConfig(data : str) -> dict:    
		DEFAULT_CONFIG = '''
		[CONFIG]
		TEST_CASE_0 = 
		TEST_CASE_N =
		N_TEST_CASES = 1
		RANDOM_MIN = 0
		RANDOM_MAX = 50
		RANDOM_FLOAT = 0
		RECURSION = FALSE
		ALLOW_LIBRARIES =
		SEPARATOR = '\a'
		COMPARE_ALL = FALSE
		EXTRA_COMPILATION = FALSE
		COMPARE_CASE_SENSITIVE = FALSE
		COMPARE_WHITE_SPACE = FALSE
		'''
		config = ConfigParser()
		config.read_string(DEFAULT_CONFIG)
		try:
			read_ini = False
			ini = ""
			for line in data.split('\n'):
				if line == "// [CONFIG]":
					read_ini = True
				elif line == "// ;EOF":
					read_ini = False
					continue
				if read_ini:
					ini += line[3:]+'\n'
			config.read_string(ini)
		except:
			logger.debug("::: Kann keine Konfiguration lesen.")
		""" Speichere alles in Dictionary """
		dconfig = dict(config.items('CONFIG'))
		dconfig['n_test_cases'] = config.getint('CONFIG', 'n_test_cases')
		dconfig['random_min'] = config.getfloat('CONFIG', 'random_min')
		dconfig['random_max'] = config.getfloat('CONFIG', 'random_max')
		dconfig['random_float'] = config.getint('CONFIG', 'random_float')
		dconfig['recursion'] = config.getboolean('CONFIG', 'recursion')
		dconfig['allow_libraries'] = config.get('CONFIG', 'allow_libraries')
		dconfig['compare_all'] = config.getboolean('CONFIG', 'compare_all')
		dconfig['compare_all'] = config.getboolean('CONFIG', 'compare_all')
		dconfig['extra_compilation'] = config.getboolean('CONFIG', 'extra_compilation')
		dconfig['compare_case_sensitive'] = config.getboolean('CONFIG', 'compare_case_sensitive')
		dconfig['compare_white_space'] = config.getboolean('CONFIG', 'compare_white_space')
		
		return dconfig
	config = readConfig(main)
	
	
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
			if re.search("[^\d][\*]\$RANDOM", case):
				logger.error("::: The configuration may be incorrect: Please check $RANDOM!")
				job.send_fail_result("Der Validator ist fehlerhaft konfiguriert!","Validator fehlerhaft konfiguriert: $RANDOM wurde falsch geschrieben!")
				quit(0)
			for found in re.findall("\d+\*\$RANDOM", case):
				case = case.replace(found,createRandom(int(found[:-8])),1)
			for found in re.findall('\$RANDOM',case):
				case = case.replace(found,createRandom(1),1)
			return tests.append(case)
		testcases= [] # create a test-list
		for key, value in config.items(): # read test-cases in config
			if 'test_case_' in key and key != 'test_case_n':
				insertRandom(value,testcases)
		if config['test_case_n']: # finally read test-case-n in config
			for n in range(0,config['n_test_cases']):
				insertRandom(config['test_case_n'],testcases)
		if testcases == []:
			logger.debug("::: No test-config found")
			return [' ']
		return testcases
		
	
		
		
	# Fuehre das Programm mehrmals mit entsprechenden cases aus
	testcases = createTests(config)	
	
	for test in testcases:
	
		# Programme ausführen
		running_example = job.spawn_program('./example', [test], timeout=5)
		running_example.sendline(test)
		exit_code_example, output_example = running_example.expect_end()

		running_submission = job.spawn_program('./submission', [test], timeout=5)
		running_submission.sendline(test)
		exit_code_submission, output_submission = running_submission.expect_end()
		
		# Security-Code prüfen
		if SECURITY_CODE in output_submission:
			job.send_fail_result("Den Validator auszulesen ist verboten! Fall wird gemeldet.","submission-output: "+output_submission)
			return
		# Exit-Codes vergleichen  
		if exit_code_example != exit_code_submission:
			job.send_fail_result("Dein Programm wurde nicht ordentlich beendet :/\nErwarteter Exit-Code: {0}\nDein Exit-Code: {1}\n\n### Erwartete Ausgabe: ###\n{2}\n\n\n### Deine Ausgabe: ###\n{3}".format(exit_code_example,exit_code_submission,output_example,output_submission),"Wrong exit-code")
			return	
		
		if re.sub('\s','',output_example.replace(config['separator'],'')) == "":
			job.send_fail_result("Validator-Fehler - Der Test erzeugt keine Ausgabe!", "Der Test erzeugt keine Ausgabe!")
			return
		if re.sub('\s','',output_submission.replace(config['separator'],'')) == "":
			job.send_fail_result("Das Programm erzeugt keine Ausgabe!")
			return
		

		# Ergebnisse der einzelnen Tests vergleichen
		output_example = output_example.split("\n",1)[1].split(config['separator'])
		output_submission = output_submission.split("\n",1)[1].split(config['separator'])
		
		output = list(zip(output_example,output_submission))
		
		for output_example, output_submission in output:
			original_example = output_example
			original_submission = output_submission
			
					
			""" Output bearbeiten """
			if not config['compare_case_sensitive']:
				output_example = output_example.lower()
				output_submission = output_submission.lower()
			
			if not config['compare_white_space']:
				output_example = re.sub('\s','',output_example)
				output_submission = re.sub('\s','',output_submission)
			
			
			print("### OUTPUT EXAMPLE: ###")
			print(output_example)
			print("### OUTPUT SUBMISSION: ###")
			print(output_submission)
			print('\n')
						
			# Output vergleichen
			try:
				if config['compare_all']:	# es werden nur Leerzeichen entfernt
					if output_example != output_submission:
						raise
				else:
					i = 0	# zusätzliche Zeichen der Abgabe werden ignoriert
					for c in output_example:
						while c != output_submission[i]:
							i += 1
						i += 1
			except:
				job.send_fail_result("Leider erzeugt dein Code eine andere Ausgabe :/\n\n### Erwartete Ausgabe: ###\n{0}\n\n\n### Deine Ausgabe: ###\n{1}".format(original_example, original_submission), "wrong output")
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
	job.send_pass_result('All tests passed. Awesome!'+hinweis, "All tests passed.\nOutput:\n\n"+output_submission)

