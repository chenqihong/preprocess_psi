'''
configuration.py: configuration of the project
'''

__author__ = "Qi Hong Chen"
__copyright__ = "Copyright 2021, the preprocess_psi_process project"

import os
import sys
from collections import defaultdict

sys.path.append("/Users/qihongchen/Desktop/")
from common_lib import *

# all_repos_directory = "/Users/qihongchen/Documents/PycharmProject/preprocess_psi_process/sources/all_repos/"
all_repos_directory = "/Users/qihongchen/Desktop/all_repos/"
PROJECT_LOG_FOLDER_PATH = "/Users/qihongchen/Documents/PycharmProject/preprocess_psi_process/logs/"
# all_repos_script_record_directory = PROJECT_LOG_FOLDER_PATH + "all_repos_code_scripts/"
all_repos_script_record_directory = "/Users/qihongchen/Desktop/all_repos_code_scripts/"
PSI_RESULT_ROOT_FOLDER_DIRECTORY = "/Users/qihongchen/Desktop/psi_result_folder_new/"
PSI_RUNNER_DIRECTORY = "/Users/qihongchen/Documents/InteliJ_Projects/scriptExtractorPluginCli"

acceptable_extensions = ['py', 'ipynb']


class CommitObject:
    def __init__(self, commit_id_1, commit_id_2, repo_name, repo_directory):
        self.commit_id_1 = commit_id_1
        self.commit_id_2 = commit_id_2
        self.repo_name = repo_name
        self.repo_directory = repo_directory
