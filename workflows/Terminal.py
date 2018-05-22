from pathlib import Path
import subprocess


class Terminal:
	def __init__(self, command, output_folder: Path, expected_output: Path):
		prefix = ""
		stdout_path = output_folder / "{}_stdout.txt".format(prefix)
		stderr_path = output_folder / "{}_stderr.txt".format(prefix)
		command_path = output_folder / "{}_command.txt".format(prefix)

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		command_path.write_text(' '.join(map(str(command))))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)

class Workflow:
	def __init__(self, program_name:str, command:List, expected_output):
		command = list(map(str,command))

		output_folder = expected_output.output_folder

		stdout_path = output_folder / "{}_stdout.txt".format(program_name)
		stderr_path = output_folder / "{}_stderr.txt".format(program_name)
		command_path = output_folder / "{}_command.txt".format(program_name)

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		command_path.write_text(' '.join(map(str(command))))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)

if __name__ == "__main__":
	pass
