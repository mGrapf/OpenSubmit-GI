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
			#relative_path = urlparse(headers["PostRunValidation"]).path		# 2020 Denz
			#job.validator_url = config.get("Server", "url") + relative_path
			job.validator_url = urlparse(headers["PostRunValidation"]).path
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
		switch_owner_of_working_directory(job)							# 2020 Denz
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
	
	from .job import Job
	job = Job(config, online=False)
	job.working_dir = create_working_dir(config, '42')

	# copy files
	if os.path.isdir(src[0]):
		src_dir = src[0]	
		for fname in glob.glob(src_dir + os.sep + '*'):
			if os.path.isfile(fname):
				logger.debug("Copying {0} to {1} ...".format(fname, job.working_dir))
				shutil.copy(fname, job.working_dir)		
	else:
		for src_file in src:
			logger.debug("Copying {0} to {1} ...".format(src_file, job.working_dir))
			if not os.path.isfile(src_file):
				logger.error("Error: File not found")
				return
			shutil.copy(src_file, job.working_dir)
			if not 'submission.cpp' in src:
				if os.path.isfile('submission.cpp'):
					logger.debug("Copying {0} to {1} ...".format('submission.cpp', job.working_dir))
					shutil.copy('submission.cpp', job.working_dir+os.sep)
				else:
					logger.debug("Copying {0} as submission.cpp to {1} ...".format(src_file, job.working_dir))
					shutil.copy(src[0], job.working_dir+os.sep+'submission.cpp')
			
		
	case_files = os.listdir(job.working_dir)
	if 'validator.py' in case_files or 'validator.zip' in case_files:
		if len(case_files) != 2:
			logger.error("Error: If the folder contains the validator.py/validator.zip, the folder may only contain 2 files.")
			return
		if case_files[0] in ['validator.py', 'validator.zip']:
			validator = job.working_dir+case_files[0]
			submission = job.working_dir+case_files[1]
		else:
			validator = job.working_dir+case_files[1]
			submission = job.working_dir+case_files[0]
		logger.debug('{0} is the validator.'.format(validator))
		logger.debug('{0} the submission.'.format(submission))
		try:
			prepare_working_directory(job,
									  submission_path=submission,
									  validator_path=validator)
		except JobException as e:
			job.send_fail_result(e.info_student, e.info_tutor)
			return None
		
	else:
		
		cpp_files = []
		for file in case_files:
			if file.endswith(".cpp"):
				cpp_files.append(file)
		
		job.student_files = None
		job.validator_files = None
		job.gi_validator = True
		if 'submission.cpp' in cpp_files:
			job.student_files = ['submission.cpp']
			logger.debug("Student files: {0}".format(job.student_files))
			cpp_files.remove('submission.cpp')
		
		if len(cpp_files) == 1:
			job.validator_files = cpp_files
		elif len(cpp_files) == 2:
			for file in cpp_files:
				with open (job.working_dir+file, "r") as cpp:
					code = cpp.read()
					if "[CONFIG]" in code and ";EOF" in code:
						logger.debug("The cpp-configuration is in "+file)
						job.validator_files = [file]
						cpp_files.remove(file)
						job.validator_files = cpp_files + job.validator_files
						break
		if not job.validator_files:
			logger.error("Error: No validator (*.cpp) found.")
			return None
		logger.debug("Validator files: {0}".format(job.validator_files))
		
		if not job.student_files:
			logger.debug("No Student files found. Copying {0} to submission.cpp".format(job.validator_files[-1]))
			shutil.copy(job.working_dir+job.validator_files[0], job.working_dir+'submission.cpp')
			job.student_files = ['submission.cpp']
		
		
	switch_owner_of_working_directory(job)						# 2020 Denz
	logger.debug("Got fake job: " + str(job))
	return job
