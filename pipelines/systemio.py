import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union

from loguru import logger


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


def get_srun_command(threads: Optional = None) -> List[Any]:
	srun_command = ["srun"]
	if threads:
		srun_command += ["--threads", threads]
	srun_command += ["--mem-per-cpu", "27000"]
	return srun_command


class CommandRunner:
	def __init__(self, logfile: Optional[Path] = None):
		if logfile:
			logfile = Path(logfile)
			if logfile.is_dir():
				logfile = logfile / "commands.sh"
		self.command_log = logfile

	def run(self, command: List[Any], output_folder: Optional[Path] = None, srun: bool = True, threads: int = 8, logonly: bool = False):
		"""
			Runs a program's command. Arguments are used to generate additional files containing the stdout, stderr,and
			command used to run the program.
		Parameters
		----------
		command: List[Any]
			The command to run. Each argument will be converted to a string.
		output_folder: Optional[Path]
			If given, the command, stdout, and stderr will be written to files in the output folder.
		threads: int; default 8
			Used to indicate the number of threads srun should use.
			This assumes that the given command includes the relevant parameter for the program being run.
		srun: bool; default False
			Whether to run the command with srun.
		logonly: bool; default = False
			If True, the given command will not be run. it will only be written to the command log. This is useful for programs that don't
			work if miniconda3 is being used, such as prokka.
		Returns
		-------
		subprocess.CompletedProcess
		"""
		if srun:
			command = get_srun_command(threads) + command
		command = format_command(command)

		start_datetime = datetime.now()
		self.write_command_to_commandlog(command)

		if logonly:
			return None

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		end_datetime = datetime.now()
		duration = (end_datetime - start_datetime).total_seconds()

		self.write_comment_to_commandlog(f"Duration: {duration:.2f} seconds.")
		self.write_line_to_commandlog("\n")

		if output_folder:
			stdout_path = output_folder / "stdout.txt"
			stderr_path = output_folder / "stderr.txt"
			command_path = output_folder / "command.txt"
			try:
				command_path.write_text(" ".join(command))
				stdout_path.write_text(process.stdout)
				stderr_path.write_text(process.stderr)
			except FileNotFoundError:
				logger.error(f"Could not write the output files to {output_folder}")

	def write_command_to_commandlog(self, command: List[str]):
		if self.command_log:
			line = " ".join(command)
			with self.command_log.open('a') as file1:
				file1.write(line + "\n")

	def write_comment_to_commandlog(self, comment: str):
		if self.command_log:
			with self.command_log.open('a') as file1:
				file1.write(f"# {comment}\n")

	def write_line_to_commandlog(self, line: str):
		if self.command_log:
			with self.command_log.open('a') as file1:
				file1.write(f"{line}\n")
	def set_command_log(self, path:Union[str,Path]):
		self.command_log = Path(path)
command_runner = CommandRunner() # Should use this object to make system calls.

def check_output(command: List[str]) -> Optional[str]:
	logger.info(f"Checking the output of {command}")
	try:
		result = subprocess.check_output(format_command(command), universal_newlines = True)
	except subprocess.CalledProcessError:
		# The command encountered an error.
		result = None
	return result


def get_anaconda_install() -> Optional[Path]:
	""" Attempts to get the anaconda install directory for the given user."""
	possible_location = Path.home() / "anaconda3" / "bin"
	return possible_location if possible_location.exists() else None


def format_command(command: Iterable[Any]) -> List[str]:
	return [str(i) for i in command]


if __name__ == "__main__":
	pass
