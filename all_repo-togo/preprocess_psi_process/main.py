#!/usr/bin/env python3

"""
Main.py main file of the project, produce psi result files
"""

__author__ = "Qi Hong Chen"
__copyright__ = "Copyright 2021, preprocess_psi_process"

from configuration import *
from util import build_commit_work_list, find_commit_id_1, find_changed_desired_files_set, extract_pure_file_name_extension, get_source_code_by_commit_id, build_psi_result_file_names, generate_psi_result_files


def work_single_repo(commit_id_list, repo_name, repo_directory):
    print("commit_id_list = ", commit_id_list)
    for commit_progress_count, (commit_id_1, commit_id_2) in enumerate(commit_id_list, 0):
        # commit_id_1 = find_commit_id_1(commit_id_2, repo_directory)
        changed_file_name_set = find_changed_desired_files_set(repo_name, commit_id_1, commit_id_2, repo_directory)
        for file_directory in changed_file_name_set:
            file_pure_file_name, file_extension = extract_pure_file_name_extension(file_directory)
            my_commit_object = CommitObject(commit_id_1, commit_id_2, repo_name, repo_directory)
            source_code_directory_v1, source_code_directory_v2 = get_source_code_by_commit_id(my_commit_object,
                                                                                              file_pure_file_name,
                                                                                              file_directory,
                                                                                              file_extension)
            psi_result_file_name_v1, psi_result_file_name_v2, psi_result_folder_directory = build_psi_result_file_names(file_pure_file_name, commit_id_1, commit_id_2, repo_name)
            generate_psi_result_files(psi_result_file_name_v1, psi_result_file_name_v2, psi_result_folder_directory, source_code_directory_v1, source_code_directory_v2)


def main():
    for repo_name in os.listdir(all_repos_directory):
        print("repo_name = ", repo_name)
        if repo_name == ".DS_Store":
            continue
        repo_directory = all_repos_directory + repo_name + '/'
        commit_id_list, total_commits = build_commit_work_list(repo_name, repo_directory)

        work_single_repo(commit_id_list, repo_name, repo_directory)


if __name__ == '__main__':
    main()

