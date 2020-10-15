'''
Internal functions related to the communication with the
OpenSubmit server.
'''

import os
import shutil
import os.path
import glob
import json

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
		fname = headers['Content-Disposition'][22:-1]
		print("DEBUG: URLRETRIEVE_FILNAME: "+fname)
		
		fullpath = path+fname
		print("DEBUG: FULLPATH: "+fullpath)
		
		if os.path.exists(fullpath):
			os.remove(fullpath)
		shutil.move(tmpfile, fullpath)
	except Exception as e:
		logger.error("Error during fetching: " + str(e))
		raise
	return fullpath

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
		return 1
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

	if not send_post(config, "/machines/", post_data):
		return 1
	return 0


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
			job.validator_url = headers["PostRunValidation"]
		job.working_dir = create_working_dir(config, job.sub_id)

		# Store submission in working directory
		submission_fname = job.working_dir + job.file_name
		with open(submission_fname, 'wb') as target:
			target.write(result.read())
		assert(os.path.exists(submission_fname))

		"""
		# Store validator package in working directory
		validator_fname = job.working_dir + 'download.validator'
		fetch(job.validator_url, validator_fname)
		"""
		""" Eigene Variante """
		try:
			validator_fname = fetch(job.validator_url, job.working_dir)
		except:
			validator_fname = job.working_dir + 'download.validator'
			fetch(job.validator_url, validator_fname)
		
		
		""" Ende Eigene Variante """

		try:
			prepare_working_directory(job, submission_fname, validator_fname)
		except JobException as e:
			job.send_fail_result(e.info_student, e.info_tutor)
			return None
		
		""" Eigene Variante """
		#if glob.glob(job.working_dir + os.sep + 'validator_example.cpp') and not glob.glob(job.working_dir + os.sep + 'validator.*'):
		#	validator = job.working_dir + os.sep +'validator.py'
		#	shutil.copy(os.path.dirname(os.path.abspath(__file__))+'/gi_validator.py', validator)
			

		""" Ende Eigene Variante """
		
		
		
		logger.debug("Got job: " + str(job))
		return job
	except HTTPError as e:
		if e.code == 404:
			logger.debug("Nothing to do.")
			return None
	except URLError as e:
		logger.error("Error while contacting {0}: {1}".format(url, str(e)))
		return None


def fake_fetch_job(config, src_dir):
	'''
	Act like fetch_job, but take the validator file and the student
	submission files directly from a directory.

	Intended for testing purposes when developing test scripts.

	Check also cmdline.py.
	'''
	logger.debug("Creating fake job from " + src_dir)
	from .job import Job
	job = Job(config, online=False)
	job.working_dir = create_working_dir(config, '42')
	for fname in glob.glob(src_dir + os.sep + '*'):
		logger.debug("Copying {0} to {1} ...".format(fname, job.working_dir))
		shutil.copy(fname, job.working_dir)
	   
	
	""" Ergaenzung fuer Grundlagen Informatik """
	if glob.glob(job.working_dir + os.sep + 'validator_example.cpp') and not glob.glob(job.working_dir + os.sep + 'validator.*'):
		validator = job.working_dir + os.sep +'validator.py'
		shutil.copy(os.path.dirname(os.path.abspath(__file__))+'/gi_validator.py', validator)
		submission = glob.glob(job.working_dir + os.sep + 'submission.cpp')
		if not submission:
			logger.debug("::: submission.cpp not found -> copy validator_example.cpp")
			shutil.copy(job.working_dir + os.sep +'validator_example.cpp', job.working_dir + os.sep +'submission.cpp')
		job.student_files = ['submission.cpp']
	else:
		""" Ende Ergaenzung """
		
		case_files = glob.glob(job.working_dir + os.sep + '*')
		assert(len(case_files) == 2)
		if os.path.basename(case_files[0]) in ['validator.py', 'validator.zip']:
			validator = case_files[0]
			submission = case_files[1]
		else:
			validator = case_files[1]
			submission = case_files[0]
		logger.debug('{0} is the validator.'.format(validator))
		logger.debug('{0} the submission.'.format(submission))
		try:
			prepare_working_directory(job,
									  submission_path=submission,
									  validator_path=validator)
		except JobException as e:
			job.send_fail_result(e.info_student, e.info_tutor)
			return None
	logger.debug("Got fake job: " + str(job))
	return job
