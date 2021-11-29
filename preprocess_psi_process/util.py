"""
uncommon_util.py: helper function of the project
"""

__author__ = "Qi Hong Chen"
__copyright__ = "Copyright 2021, the keywords_filter_psi project"

from typing import TextIO
from configuration import *


def create_folder_safely_helper(folder_directory: str) -> None:
    """
    Safely Create Given Folder, sub function of setup function in uncommon_util.py
    :param: folder_directory: Full Directory of folder
    """
    try:
        os.mkdir(folder_directory)
    except FileExistsError:
        os.rmdir(folder_directory)
        os.mkdir(folder_directory)


def setup() -> None:
    """
    Create Progress report and create log files folder and csv result folder and load keyword list
    :return: None
    """
    create_folder_safely_helper(all_repos_script_record_directory)


def extract_commit_id_list_from_git_log_result(log_cache_directory: str) -> list:
    """
    extract commit_id_list from the git log command, helper function of the build_commit_work_list in uncommon_util.py
    :param log_cache_directory: The result of git log command result file
    :return: [sha1, sha2, sha3 ...]
    """
    commit_id_list = list()
    with open(log_cache_directory, 'r') as my_file:
        for line in my_file:
            commit_id = line.strip().split(' ')[0].strip()
            commit_id_list.append(commit_id)
    commit_id_list.reverse()
    return commit_id_list


# def build_commit_work_list(repo_name: str, repo_directory: str) -> tuple:
#     """
#     Build the commit list for each repo
#     :param repo_name: name of the repo
#     :param repo_directory: full directory of the repo
#     :return: [sha1, sha2, sha3....], total number_of_commits
#     """
#     log_cache_directory = all_repos_script_record_directory + repo_name + "_log_cache.txt"
#     git_log_command = "git -C {}".format(repo_directory) + " log --pretty=oneline > {}".format(log_cache_directory)
#     os.system(git_log_command)
#     commit_id_list = extract_commit_id_list_from_git_log_result(log_cache_directory)
#     os.remove(log_cache_directory)
#     commit_id_list = commit_id_list[1:]
#     return commit_id_list, len(commit_id_list)


def get_commit_message_helper(repo_name, commit_id, repo_directory):
    '''
    Given a commit id for a repo name, returns its commit msg
    :param: repo_name:
    :param: commit_id:
    :param: repo_directory:
    :return: commit_msg
    '''
    commit_message_file_directory = all_repos_script_record_directory + repo_name + "_commit_msg.txt"
    commit_message_command = "git -C {}".format(repo_directory) + " show -s {}".format(commit_id) + " > {}".format(
        commit_message_file_directory)
    os.system(commit_message_command)
    last_count = 0
    new_str = ""
    with open(commit_message_file_directory, 'r') as f:
        for count, line in enumerate(f, 0):
            if line.split(' ')[0] == 'Date:':
                last_count = count
            elif last_count != 0 and count > last_count:
                new_str += line.strip() + '\n'
        new_str = new_str.strip()
    os.remove(commit_message_file_directory)
    return new_str


def build_commit_work_list(repo_name: str, repo_directory: str) -> tuple:
    '''
    Build the commit_list from earliest to newest, and skip the merge once
    :param: repo_name: name of the repo
    :param: repo_directory: full directory of the repo
    :return: [(sha1, sha2), (sha2, sha3), (sha3, sha4).... ], total_number_of_pairs
    '''
    log_cache_directory = all_repos_script_record_directory + repo_name + "_log_cache.txt"
    git_log_command = "git -C {}".format(repo_directory) + " log --pretty=oneline > {}".format(log_cache_directory)
    os.system(git_log_command)
    commit_id_list = list()
    work_load_list = list()
    with open(log_cache_directory, 'r') as my_file:
        for line in my_file:
            commit_id = line.strip().split(' ')[0].strip()
            commit_id_list.append(commit_id)
    commit_id_list.reverse()

    for count in range(len(commit_id_list)):
        if count <= len(commit_id_list) - 2:
            work_load_list.append([commit_id_list[count], commit_id_list[count + 1]])
    filtered_commit_id_list = list()
    for commit_id_1, commit_id_2 in work_load_list:
        commit_msg_2 = get_commit_message_helper(repo_name, commit_id_2, repo_directory)
        if 'Merge pull request ' in commit_msg_2 or 'Merge branch ' in commit_msg_2:
            continue
        filtered_commit_id_list.append((commit_id_1, commit_id_2))
    os.remove(log_cache_directory)
    return filtered_commit_id_list, len(filtered_commit_id_list)


def find_commit_id_1(commit_id: str, repo_directory: str) -> str:
    """
    Given the commit id, find its parent. Sub function of the build_csv_current_row in csv_util.py
    :param commit_id: sha2
    :param repo_directory: directory of the working repo
    :return: sha1
    """
    git_extract_parent_commit_id_file_directory = all_repos_script_record_directory + "extract_parent_result.txt"
    trace_parent_commit_id_command = "git -C {}".format(repo_directory) + " rev-parse {}".format(commit_id) + '^ > {}'.format(git_extract_parent_commit_id_file_directory)
    os.system(trace_parent_commit_id_command)
    commit_id_1 = "error"
    with open(git_extract_parent_commit_id_file_directory, 'r') as f:
        for line in f:
            if not line.strip().startswith("fatal: cannot change to"):
                commit_id_1 = line.strip()
    os.remove(git_extract_parent_commit_id_file_directory)
    return commit_id_1


def find_changed_desired_files_set(repo_name: str, commit_id_1: str, commit_id_2: str, repo_directory: str) -> set:
    """
    Given a repo and its commit, find all its changed files that are python or ipynb files
    :param repo_name: The name of the repo
    :param commit_id_1: sha1
    :param commit_id_2: sha2
    :param repo_directory: full repo directory
    :return: [a.py, b.py, /model/c.py]
    """
    diff_files_directory = all_repos_script_record_directory + repo_name + "_diff_files.txt"
    diff_command = "git -C {}".format(repo_directory) + " diff --name-only {}".format(commit_id_1) + " {}".format(
        commit_id_2) + " > {}".format(diff_files_directory)
    os.system(diff_command)
    changed_file_set = set()
    with open(diff_files_directory) as my_file:
        for file_name in my_file:
            file_name = file_name.strip()
            pure_file_name = file_name
            if '/' in file_name:
                pure_file_name = file_name.split('/')[-1]
            if is_ds_store(pure_file_name) or is_non_extension_file(pure_file_name):
                continue
            extension = pure_file_name.split(".")[-1]
            if extension in acceptable_extensions:
                changed_file_set.add(file_name)
    os.remove(diff_files_directory)
    return changed_file_set


def extract_pure_file_name_extension(python_file_directory: str) -> tuple:
    """
    Given a file directory, extract its pure file name and extension
    input: /ISR/models/cut_vgg19.py
    output: cut_vgg19, py
    :param python_file_directory: file full path
    :return: tuple
    """
    python_name = python_file_directory.split('/')[-1].split('.')[0]
    extension = python_file_directory.split('/')[-1].split('.')[-1]
    if ")" in python_name or '(' in python_name:
        split_by_space_list = python_name.split(' ')
        left = split_by_space_list[0]
        right = split_by_space_list[1]
        if ')' in left:
            python_name = right.strip()
        else:
            python_name = python_name.split("(")[0].strip()
    return python_name, extension


def build_source_code_file_directory(file_directory: str, python_pure_file_name: str, file_extension: str) -> str:
    """
    Find the python file directory used in git show to get the script code of a commit of a repo
    :param file_directory: The file directory of the changed file in repo (not previous version code): model/a.py
    :param python_pure_file_name: the pure file name: a
    :param file_extension: py
    :return: the changed_file_directory_for_getting_commit_code
    """
    result_directory = ""
    directory_split_list = file_directory.split('/')[:-1]
    for i in directory_split_list:
        result_directory += i + '/'
    result_directory = result_directory + python_pure_file_name + '.' + file_extension
    return result_directory


def get_source_code_by_commit_id(my_commit_object: CommitObject, changed_file_pure_file_name: str, file_directory: str,
                                 file_extension: str) -> tuple:
    """
    Get the commit script code of a repo's commits
    :param my_commit_object: The object contains the commit information
    :param changed_file_pure_file_name: The changed python file's pure file name
    :param file_directory: The changed python file's file directory
    :param file_extension: The extension of the file: py or ipynb
    :return: tuples of file directory: (file_old_version1.py, file_old_version2.py)
    """
    file_content_directory_v1 = all_repos_script_record_directory + my_commit_object.repo_name + '_' + changed_file_pure_file_name + "_v1.py"
    file_content_directory_v2 = all_repos_script_record_directory + my_commit_object.repo_name + "_" + changed_file_pure_file_name + "_v2.py"
    set_up_limit_command = "git -C {}".format(my_commit_object.repo_directory) + " config diff.renameLimit 99999"
    os.system(set_up_limit_command)
    processed_python_file_directory = build_source_code_file_directory(file_directory, changed_file_pure_file_name,
                                                                       file_extension)

    file_content_command_v1 = "git -C {}".format(my_commit_object.repo_directory) + " show {}".format(
        my_commit_object.commit_id_1) + ":{}".format(processed_python_file_directory) + " &> {}".format(
        file_content_directory_v1)

    file_content_command_v2 = "git -C {}".format(my_commit_object.repo_directory) + " show {}".format(
        my_commit_object.commit_id_2) + ":{}".format(processed_python_file_directory) + " &> {}".format(
        file_content_directory_v2)

    os.system(file_content_command_v1)
    os.system(file_content_command_v2)
    return file_content_directory_v1, file_content_directory_v2


def build_psi_result_file_names(file_pure_file_name, commit_id_1, commit_id_2, repo_name):
    result_folder_directory = PSI_RESULT_ROOT_FOLDER_DIRECTORY + repo_name + '/'
    before_file_name = file_pure_file_name + '_' + commit_id_1 + "_" + "v1" + '.' + "txt"
    after_file_name = file_pure_file_name + '_' + commit_id_2 + '_' + "v2" + '.' + "txt"
    return before_file_name, after_file_name, result_folder_directory


def generate_psi_result_files(psi_result_file_name_v1, psi_result_file_name_v2, psi_result_folder_directory, source_code_directory_v1, source_code_directory_v2):
    os.chdir(PSI_RUNNER_DIRECTORY)
    source_code_project_directory = ''
    directory_split_list = source_code_directory_v1.split('/')[:-1]
    for i in directory_split_list:
        source_code_project_directory += i + '/'
    source_code_file_name_v1 = source_code_directory_v1.split('/')[-1]
    source_code_file_name_v2 = source_code_directory_v2.split('/')[-1]
    if not os.path.isdir(psi_result_folder_directory):
        os.mkdir(psi_result_folder_directory)
    generate_file1_command = "python3 runner.py {}".format(source_code_project_directory) + ' {}'.format(source_code_file_name_v1) + ' {}'.format(psi_result_folder_directory + psi_result_file_name_v1)
    print("generate_file1_command = ", generate_file1_command)
    os.system(generate_file1_command)
    generate_file2_command = "python3 runner.py {}".format(source_code_project_directory) + ' {}'.format(source_code_file_name_v2) + ' {}'.format(psi_result_folder_directory + psi_result_file_name_v2)
    os.system(generate_file2_command)



