# Administration script functionality on the production system

import sys

from . import CONFIG_FILE_DEFAULT
from .server import fetch_job, fake_fetch_job, send_hostinfo
from .running import kill_longrunning
from .locking import ScriptLock, break_lock
from .config import read_config, has_config, create_config, check_config
from time import sleep

def download_and_run(config):
    '''
    Main operation of the executor.

    Returns True when a job was downloaded and executed.
    Returns False when no job could be downloaded.
    '''
    job = fetch_job(config)
    if job:
        job._run_validate()
        return True
    else:
        return False


def copy_and_run(config, src_dir):
    '''
    Local-only operation of the executor.
    Intended for validation script developers,
    and the test suite.

    Please not that this function only works correctly
    if the validator has one of the following names:
        - validator.py
        - validator.zip

    Returns True when a job was prepared and executed.
    Returns False when no job could be prepared.
    '''
    job = fake_fetch_job(config, src_dir)
    if job:
        job._run_validate()
        return True
    else:
        return False



def console_script():
    '''
        The main entry point for the production
        administration script 'opensubmit-exec',
        installed by setuptools.
    '''

    if len(sys.argv)==1 or sys.argv[1] not in ['configcreate','configtest','run','run_every','test','unlock','help']:
        print("usage: opensubmit-exec [configcreate <server_url>|configtest|run|test <dir>|unlock|help] [-c config_file]")
        return 0
    
    # Translate legacy commands
    if sys.argv[1] == "configure":
        sys.argv[1] = 'configtest'

    # get config-file
    config_fname = CONFIG_FILE_DEFAULT
    for index, entry in enumerate(sys.argv):
        if entry == "-c" and index < len(sys.argv)-1:
            config_fname= sys.argv[index + 1]
            break
    
    if sys.argv[1] == "help":
        print("configcreate <server_url>:  Create initial config file for the OpenSubmit executor")
        print("configtest:                 Check config file for correct installation of the OpenSubmit executor")
        print("run:                        Fetch and run code to be tested from the OpenSubmit web server once. Suitable for crontab")
        print("run_every <seconds>:        Fetch and run code to be tested from the OpenSubmit web server every n seconds.")
        print("test <dir>:                 Run test script from a local folder for testing purposes")
        print("unlock:                     Break the script lock, because of crashed script")
        print("help:                       Print this help")
        print("-c <config_file>            Configuration file to be used (default: {0})".format(CONFIG_FILE_DEFAULT))
        return 0
    
    if sys.argv[1] == "configcreate":
        if len(sys.argv)<=2 or sys.argv[2][0] == '-':
            print("usage: opensubmit-exec configcreate <server_url> [-c <config_file>]")
            return 1
        server_url = sys.argv[2]
        
        print("Creating config file at " + config_fname)
        if create_config(config_fname, override_url=server_url):
            print("Config file created, fetching jobs from " + server_url)
            return 0

    if sys.argv[1] == "configtest":
        if not has_config(config_fname):
            print("ERROR: Seems like the config file \"%s\" does not exist. Call 'opensubmit-exec configcreate <server_url>' first." % config_fname)
            return 1    
        config = read_config(config_fname)
        if not check_config(config):
            return 1
        
        print("Sending host information update to server ...")
        if not send_hostinfo(config):
            return 1
        return 0

    if sys.argv[1] == "unlock":
        config = read_config(config_fname)
        break_lock(config)
        return 0

    if sys.argv[1] == "run_old":
        config = read_config(config_fname)
        # Perform additional precautions for unattended mode in cron
        kill_longrunning(config)
        
        jobs = True
        while jobs:
            with ScriptLock(config):
                jobs = download_and_run(config)
        return 0
    
    if sys.argv[1] == "run":
        config = read_config(config_fname)
        kill_longrunning(config)
        repeat_time = config.getint('Execution', 'repeat_time')
        while(True):
            try:
                jobs = True
                while jobs:
                    jobs = download_and_run(config)
            except Exception as e:
                print(e)
            sleep(repeat_time)
        return 0
        
    if sys.argv[1] == "run_every":
        if len(sys.argv)<=2 or sys.argv[2][0] == '-' or not sys.argv[2].isdecimal():
            print("usage: opensubmit-exec run_every <seconds> [-c <config_file>]")
            return 1
        seconds = int(sys.argv[2])
        
        config = read_config(config_fname)
        kill_longrunning(config)
        
        while(True):
            try:
                jobs = True
                while jobs:
                    with ScriptLock(config):
                        jobs = download_and_run(config)
            except Exception as e:
                print(e)
            sleep(seconds)
        return 0
            
    if sys.argv[1] == "test":
        if len(sys.argv)<=2 or sys.argv[2][0] == '-':
            print("usage: opensubmit-exec test <dir> [-c <config_file>]")
            return 1
        config = read_config(config_fname)
        copy_and_run(config, sys.argv[2])
        return 0


if __name__ == "__main__":
    exit(console_script())
