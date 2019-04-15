import argparse

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from dataclasses import asdict, dataclass

# noinspection PyProtectedMember
SubparserType = Optional[argparse._SubParsersAction]


@dataclass
class ProgramLocations:
	fastqc: str = "fastqc"
	trimmomatic: str = "trimmomatic"
	spades: str = 'spades.py'
	prokka: str = "prokka"
	bandage: str = "/home/cld100/Bandage-0.8.1/Bandage"

	def get_version_information(self) -> Dict[str, str]:
		versions = dict()
		for key, value in asdict(self).items():
			cmd = [value, '--version']
			process = subprocess.run(cmd, stdout = subprocess.PIPE)
			versions[key] = process.stdout
		return versions


programs = ProgramLocations()


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


@dataclass
class WorkflowOptions:
	trimmomatic_location: Path


def get_srun_command(threads: Optional = None) -> List[Any]:
	srun_command = ["srun"]
	if threads:
		srun_command += ["--threads", threads]
	srun_command += ["--mail-user=cld100@pitt.edu", "--mail-type=end,fail"]
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


def run_command(program_name: str, command: List[Any], output_folder: Path,
		threads: Tuple[str, int] = None, use_srun: bool = True) -> subprocess.CompletedProcess:
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
	use_srun: bool; default False
		Whether to run the command with srun.

	Returns
	-------
	subprocess.CompletedProcess
	"""
	logger.info(f"{program_name} - Running command " + str(command))
	if threads:
		num_threads = threads[1]
		command = command[:1] + [*threads] + command[1:]
	else:
		num_threads = None
	if use_srun:
		command = get_srun_command(num_threads) + command

	stdout_path = output_folder / "{}_stdout.txt".format(program_name)
	stderr_path = output_folder / "{}_stderr.txt".format(program_name)
	command_path = output_folder / "{}_command.txt".format(program_name)
	command = list(map(str, command))
	output_folder_already_exists = output_folder.exists()
	if output_folder_already_exists:
		try:
			command_path.write_text(' '.join(command))
		except FileNotFoundError:
			# Path(__file__).with_name('debug_command.txt').write_text(' '.join(command))
			logger.warning("Cannot write to ", command_path)
	start_datetime = datetime.now()
	logger.info("Running Command")
	for element in command:
		if element.startswith('-'):
			logger.info(f"\t{element}")
		else:
			logger.info(f"\t\t{element}")
	process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

	end_datetime = datetime.now()
	duration = end_datetime - start_datetime
	logger.info(f"Finished command. Duration: {duration}")
	command_string = "{}\n\nstart: {}\nend: {}\nduration: {}\n".format(
		' '.join(command), start_datetime, end_datetime, duration
	)

	try:
		command_path.write_text(command_string)
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)
	except FileNotFoundError as exception:
		Path(__file__).with_name('debug_stdout.txt').write_text(process.stdout)
		Path(__file__).with_name('debug_stderr.txt').write_text(process.stderr)
		Path(__file__).with_name('debug_command.txt').write_text(command_string)
		raise exception
	return process


if __name__ == "__main__":
	pass
