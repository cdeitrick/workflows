import subprocess
from pathlib import Path
from typing import Any, List,Tuple, Optional

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


def get_srun_command(threads:Optional = None)->List[Any]:

	srun_command = ["srun"]
	if threads:
		srun_command += ["-t", threads]
	srun_command += ["--mail-user=cld100@pitt.edu", "--mail-type=all"]
	return srun_command

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


def run_command(program_name: str, command: List[Any], output_folder: Path, threads:Tuple[str,int] = None) -> subprocess.CompletedProcess:
	"""
		Runs a program's command. Arguments are used to generate additional files containing the stdout, stderr,and
		command used to run the program.
	Parameters
	----------
	program_name
	command
	output_folder
	threads: Tuple[str,int]
		Used to indicate the number of threads srun should use.
		It should ba a tuple of the program's threads flag and the number of threads.
		ex. ('--threads', 8)
		ex. ('-j', 16)

	Returns
	-------
	subprocess.CompletedProcess
	"""

	if threads:
		num_threads = threads[1]
		command = command[:1] + [*threads] + command[1:]
	else:
		num_threads = None

	command = get_srun_command(num_threads) + command
	command = list(map(str, command))

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
