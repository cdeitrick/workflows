import subprocess
from pathlib import Path
from typing import Any, List

from dataclasses import dataclass


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


@dataclass
class Sample:
	name: str
	forward: Path
	reverse: Path
	folder: Path

	def exists(self):
		return self.forward.exists() and self.reverse.exists()


srun_command = ["srun", "--threads", "16", "--mail-user=cld100@pitt.edu", "--mail-type=all"]


def get_output_folder(name: str, make_dirs: bool = True, **kwargs) -> Path:
	"""
		Attempts to generate the expected output folder.
	Parameters
	----------
	name:str
	make_dirs:bool
	kwargs

	Returns
	-------
	Path
	"""
	output_folder = kwargs.get("output_folder")
	if not output_folder:
		parent_folder = kwargs['parent_folder']
		output_folder = parent_folder / "{}_output".format(name)
		if make_dirs:
			checkdir(output_folder)

	return output_folder


def clean_command_arguments(command: List[Any]) -> List[str]:
	command = srun_command + command
	command = list(map(str, command))
	return command


def run_command(program_name: str, command: List[Any], output_folder: Path) -> subprocess.CompletedProcess:
	"""
		Runs a program's command. Arguments are used to generate additional files containing the stdout, stderr,and
		command used to run the program.
	Parameters
	----------
	program_name
	command
	output_folder

	Returns
	-------
	subprocess.CompletedProcess
	"""

	command = clean_command_arguments(command)
	print(command)
	process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

	stdout_path = output_folder / "{}_stdout.txt".format(program_name)
	stderr_path = output_folder / "{}_stderr.txt".format(program_name)
	command_path = output_folder / "{}_command.txt".format(program_name)

	command_path.write_text(' '.join(command))
	stdout_path.write_text(process.stdout)
	stderr_path.write_text(process.stderr)

	return process


if __name__ == "__main__":
	pass
