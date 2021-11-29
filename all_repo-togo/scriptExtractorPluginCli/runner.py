import subprocess
from pathlib import Path
import sys

_, project, file_name, output_file_directory = sys.argv
# project = "/Users/qihongchen/PycharmProjects/pythonProject/"
# file_name = 'main.py'
print("sys.argv = ", sys.argv)
print("project = ", project)
print("file_name = ", file_name)
print("output file directory = ", output_file_directory)
PLUGIN_ROOT = Path("/Users/qihongchen/Documents/InteliJ_Projects/scriptExtractorPluginCli/")


process = subprocess.run([PLUGIN_ROOT / 'gradlew', '-p', str(PLUGIN_ROOT), 'runIde', f'-PprojectDirectory={project}', f'-PfileName={file_name}', f'-PoutputFileDirectory={output_file_directory}'], capture_output=True,text=True)
print("process = ", process)