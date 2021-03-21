'''
Internal functions related to the communication with the
OpenSubmit server.
'''

import os
import shutil
import os.path
import glob
import json
import re
from .exceptions import *
from .filesystem import *
from .hostinfo import ipaddress, all_host_infos

from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import logging
logger = logging.getLogger('opensubmitexec')


def fetch(url, path):
	'''
	Fetch data from an URL and save it under the given target name.
	'''
	logger.debug("Fetching %s from %s" % (path, url))

	try:
		tmpfile, headers = urlretrieve(url)
		fname = headers['Content-Disposition'].split('filename=')[1].replace('\"','')	# 2020 Denz: read filename from header
		if fname.rfind('.') != -1:
			fname = 'validator.'+fname.rsplit('.',1)[1]
		fullpath = path + fname
		if os.path.exists(fullpath):
			os.remove(fullpath)
		shutil.move(tmpfile, fullpath)
	except Exception as e:
		logger.error("Error during fetching: " + str(e))
		raise
	return fullpath														# 2020 Denz: return path with filename

def send_post(config, urlpath, post_data):
	'''
	Send POST data to an OpenSubmit server url path,
	according to the configuration.
	'''
	server = config.get("Server", "url")
	logger.debug("Sending executor payload to " + server)
	post_data = urlencode(post_data)
	post_data = post_data.encode("utf-8", errors="ignore")
	url = server + urlpath
	try:
		urlopen(url, post_data)
	except Exception as e:
		logger.error('Error while sending data to server: ' + str(e))
		return -1														# 2020 Denz: add return for docker-entry.sh
	return 0


def send_hostinfo(config):
	'''
	Register this host on OpenSubmit test machine.
	'''
	info = all_host_infos()
	logger.debug("Sending host information: " + str(info))
	post_data = [("Config", json.dumps(info)),
				 ("Action", "get_config"),
				 ("UUID", config.get("Server", "uuid")),
				 ("Address", ipaddress()),
				 ("Secret", config.get("Server", "secret"))
				 ]

	return send_post(config, "/machines/", post_data)					# 2020 Denz: add a return for docker-entry.sh


def compatible_api_version(server_version):
	'''
	Check if this server API version is compatible to us.
	'''
	try:
		semver = server_version.split('.')
		if semver[0] != '1':
			logger.error(
				'Server API version (%s) is too new for us. Please update the executor installation.' % server_version)
			return False
		else:
			return True
	except Exception:
		logger.error(
			'Cannot understand the server API version (%s). Please update the executor installation.' % server_version)
		return False

def fetch_job(config):
	'''
	Fetch any available work from the OpenSubmit server and
	return an according job object.

	Returns None if no work is available.

	Errors are reported by this function directly.
	'''
	url = "%s/jobs/?Secret=%s&UUID=%s" % (config.get("Server", "url"),
										  config.get("Server", "secret"),
										  config.get("Server", "uuid"))

	try:
		# Fetch information from server
		result = urlopen(url)
		headers = result.info()
		logger.debug("Raw job data: " + str(result.headers).replace('\n', ', '))
		if not compatible_api_version(headers["APIVersion"]):
			# No proper reporting possible, so only logging.
			logger.error("Incompatible API version. Please update OpenSubmit.")
			return None

		if headers["Action"] == "get_config":
			# The server does not know us,
			# so it demands registration before hand.
			logger.info("Machine unknown on server, sending registration ...")
			send_hostinfo(config)
			return None

		# Create job object with information we got
		from .job import Job
		job = Job(config)

		job.submitter_name = headers['SubmitterName']
		job.author_names = headers['AuthorNames']
		job.submitter_studyprogram = headers['SubmitterStudyProgram']
		job.course = headers['Course']
		job.assignment = headers['Assignment']
		job.action = headers["Action"]
		job.file_id = headers["SubmissionFileId"]
		job.sub_id = headers["SubmissionId"]
		job.file_name = headers["SubmissionOriginalFilename"]
		job.submitter_student_id = headers["SubmitterStudentId"]
		if "Timeout" in headers:
			job.timeout = int(headers["Timeout"])
		if "PostRunValidation" in headers:
			# Ignore server-given host + port and use the configured one instead
			# This fixes problems with the arbitrary Django LiveServer port choice
			# It would be better to return relative URLs only for this property,
			# but this is a Bernhard-incompatible API change
			from urllib.parse import urlparse
			
			job.validator_url = headers["PostRunValidation"]			# 2020 Denz: Better for sub-addresses
		job.working_dir = create_working_dir(config, job.sub_id)

		# Store submission in working directory
		submission_fname = job.working_dir + job.file_name
		with open(submission_fname, 'wb') as target:
			target.write(result.read())
		assert(os.path.exists(submission_fname))

		# Store validator package in working directory
		validator_fname = fetch(job.validator_url, job.working_dir)		# 2020 Denz: Path/Filename from header


		try:
			prepare_working_directory(job, submission_fname, validator_fname)
		except JobException as e:
			job.send_fail_result(e.info_student, e.info_tutor)
			return None
		logger.debug("Got job: " + str(job))
		return job
	except HTTPError as e:
		if e.code == 404:
			logger.debug("Nothing to do.")
			return None
	except URLError as e:
		logger.error("Error while contacting {0}: {1}".format(url, str(e)))
		return None


def fake_fetch_job(config, src):
	'''
	Act like fetch_job, but take the validator file and the student
	submission files directly from a directory.

	Intended for testing purposes when developing test scripts.

	Check also cmdline.py.
	'''
	
	# 2021 Files can be specified directly or through a directory.
	if all([os.path.isfile(f) for f in src]):
		case_files = src
		src_path = '.'+os.sep
	elif os.path.isdir(src[0]):
		case_files = [f for f in os.listdir(src[0]) if os.path.isfile(src[0]+os.sep+f)]
		src_path = src[0]+os.sep
	else:
		
		print("usage: \t\"opensubmit-exec test <dir>\" \nor: \t\"opensubmit-exec test <file_1> <file_2> ...\"")
		return
	files = [f for f in case_files if f.endswith(".zip") or f.endswith("cpp") or f.endswith("py")]
	if not files:
		print("There are no files!")
		return
	
	
	logger.debug("Creating fake job from " + str(case_files))
	from .job import Job
	job = Job(config, online=False)
	job.working_dir = create_working_dir(config, '42')
	for fname in case_files:
		logger.debug("Copying {0} to {1} ...".format(fname, job.working_dir))
		shutil.copy(src_path+fname, job.working_dir)
	
	# unpack zip files
	zip_files = [f for f in os.listdir(job.working_dir) if f.endswith(".zip")]
	for file in zip_files:
		unpack_if_needed(job.working_dir, job.working_dir+file)
	case_files = os.listdir(job.working_dir)
	
	# Test whether the standard Python validator is used.
	if 'validator.py' in case_files:
		validator = 'validator.py'
		case_files.remove(validator)	
		if case_files:
			submission = case_files[0]
		else:
			logger.error("Can't find a submission.")
			return None
		logger.debug('{0} is the validator and {1} the submission.'.format(validator,submission))
		try:
			prepare_working_directory(job,submission_path=job.working_dir+submission,validator_path=job.working_dir+validator)
		except JobException as e:
			job.send_fail_result(e.info_student, e.info_tutor)
			return None
		logger.debug("Got fake job: " + str(job))
		return job
	


	# Test wether GI validator is used.
	cpp_files = [f for f in os.listdir(job.working_dir) if f.endswith(".cpp")]
	if cpp_files:
		logger.debug("Try to select an example.cpp for the gi-validator from: {0}".format(cpp_files))
		job.cpp_example, job.cpp_main, job.cpp_config = find_cpp_config(job.working_dir, cpp_files)	
		if job.cpp_example:
			
			# Prepare submission
			cpp_files = [f for f in os.listdir(job.working_dir) if f.endswith(".cpp")]
			cpp_files.remove(job.cpp_example)
			cpp_files.remove(job.cpp_main)
			if len(cpp_files) == 1:
				job.cpp_submission = cpp_files[0]
			elif len(cpp_files) == 0:
				job.cpp_submission = "fake-submission.cpp"
				logger.debug("Create fake submission cpp: {0}".format(job.cpp_submission))
				shutil.copy(job.working_dir+job.cpp_example, job.working_dir+job.cpp_submission)
			else:
				print("Which cpp-file ist the submission?")
				for i in range(len(cpp_files)):
					print("\t[{0}] {1}".format(i+1,cpp_files[i]))
				i = None
				while i not in range(len(cpp_files)):
					print("Please select a Number of an available file: ",end='')
					try:
						i = int(input())-1     
					except ValueError:
						print("Wrong input. ",end='')
				job.cpp_submission = cpp_files[i]
				
			switch_owner_of_working_directory(job)
			
			job.student_files = [job.cpp_submission]
			
			
			logger.debug("cpp_example: {0}".format(job.cpp_example))
			logger.debug("cpp_main: {0}".format(job.cpp_main))
			logger.debug("cpp_submission: {0}".format(job.cpp_submission))
			logger.debug("Got fake job: " + str(job))
			job.gi_validator = True
			return job
		else:
			logger.debug("Fail")
		

	logger.error("Can't find a Validator.")
	return None
				
		



