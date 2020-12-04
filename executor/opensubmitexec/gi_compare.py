#!/usr/bin/env python
import re

def compare(output_example : str, output_submission : str, config : {}):
	# compare_case_sensitive
	if not config['compare_case_sensitive']:
		output_example = output_example.lower()
		output_submission = output_submission.lower()
	
	# Whitespaces am Anfang und am Ende entfernen
	output_example = output_example.strip()
	output_submission = output_submission.strip()

	# Schreibe Output je nach Modus in Liste
	if config['comparison_mode'] == 0:
		output_example = [output_example]
		output_submission = [output_submission]
	if config['comparison_mode'] == 1:
		output_example = output_example.split('\n')
		output_submission = output_submission.split('\n')
	elif config['comparison_mode'] == 2:
		output_example = output_example.split()
		output_submission = output_submission.split()
	elif config['comparison_mode'] == 3:
		output_example = list(output_example)
		output_submission = list(output_submission)

	# example veraendern
	for i in range(len(output_example)):
		if config['compare_only_numbers']:
			output_example[i] = re.sub('[^0-9]+','',output_example[i])
		if config['compare_spaces']:
			output_example[i] = output_example[i].rstrip() # nur rechte Leerzeichen entfernen
		else:
			output_example[i] = re.sub("\s","",output_example[i]) # alle Leerzeichen entfernen
	output_example = [feld for feld in output_example if feld != ''] # leere Listeneintraege entfernen
	if len(output_example) == 0:
		return False, "Validatorfehler: Der Test erzeugt mit der aktuellen Konfiguration keine sinnvolle Ausgabe!"
	
	# submission veraendern
	for i in range(len(output_submission)):
		if config['compare_only_numbers']:
			output_submission[i] = re.sub('[^0-9]+','',output_submission[i])
		if config['compare_spaces']:
			output_submission[i] = output_submission[i].rstrip() # nur rechte Leerzeichen entfernen (bei Zeilen)
		else:
			output_submission[i] = re.sub("\s","",output_submission[i]) # alle Leerzeichen entfernen
	output_submission = [feld for feld in output_submission if feld != ''] # leere Listeneintraege entfernen
	if len(output_submission) == 0:
		return False, "Das Programm erzeugt keine Ausgabe!"

	
	print("\n### Bearbeitet: Example: ###")
	for e in output_example:
		print('|'+e+'|')
	print("### Bearbeitet: Submission: ###")
	for e in output_submission:
		print('|'+e+'|')
	print()
	
	
	if config['comparison_mode'] == 0: # Vergleich Mode 0:
		pos = output_submission[0].find(output_example[0])
		if config['compare_skip_first'] and pos > 0:
			output_submission[0] = output_submission[0][pos:]
		if (config['compare_skip'] != 0 and pos == -1) \
		or (config['compare_skip'] == 0 and output_example[0] != output_submission[0]):
			return False, "Nicht gleich (1)"
	else: # Vergleich Mode 1-3:
		if config['compare_skip_first']:
			for s in output_submission:
				if s not in output_example:
					output_submission.remove(s)
					break
		if config['compare_any_order']:
			for e in output_example:
				try:
					output_submission.remove(e)
				except:
					return False, "Nicht gleich (2)"
		else:
			i = 0
			for e in output_example:
				if i >= len(output_submission):
					return False, "Nicht gleich (3)"
				while(e != output_submission[i] and i+1 < len(output_submission)):
					i += 1
				if e == output_submission[i]:
					output_submission.pop(i)
				else:
					return False, "Nicht gleich (4)"
	
		skip = config['compare_skip']
		length = len(output_submission)
		if skip >= 0 and length > skip:
			return False, "Nicht gleich (5). "+str(length-skip)+" zu viel!"

	return True, "Output ist gleich!"


if __name__ == "__main__":
	output_example = '''

Hallo Welt!
Hier ist ein Text
In welchem Zahlen, wie 1, 2 oder auch 42 vorkommen können.
9 7 3
111 2
Ende'''
	output_submission = '''
	er
	ff
	ferfe
	Hallo Welt!
	  Hier ist ein Text
	In welchem Zahlen, wie 1, 2 oder auch 42 vorkommen können.
	9 7 3
	 111 2

	 Ende

	'''
	print("### Example: ###")
	for e in output_example.split('\n'):
		print('|'+e+'|')
	print("### ######## ###")
	print("### Submission: ###")
	for e in output_submission.split('\n'):
		print('|'+e+'|')
	print("### ######## ###")
	
	
	config = {}
	config['comparison_mode'] = 1
	config['compare_skip'] = 0
	config['compare_skip_first'] = True
	config['compare_any_order'] = False
	config['compare_spaces'] = False
	config['compare_case_sensitive'] = False
	config['compare_only_numbers'] = False
	

	
	
	
	
	result, text = compare(output_example,output_submission,config)
	print(result)
	print(text)

