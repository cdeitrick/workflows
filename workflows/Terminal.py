from pathlib import Path
import subprocess
from typing import List, Any, Callable, Tuple

try:
	from . import common
except:
	import common


def clean_command_arguments(command: List[Any]) -> List[str]:
	command = common.srun_command + command
	command = list(map(str, command))
	return command


def run_command(program_name: str, command: List[Any], output_folder: Path):
	command = clean_command_arguments(command)
	process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

	stdout_path = output_folder / "{}_stdout.txt".format(program_name)
	stderr_path = output_folder / "{}_stderr.txt".format(program_name)
	command_path = output_folder / "{}_command.txt".format(program_name)

	command_path.write_text(' '.join(map(str, command)))
	stdout_path.write_text(process.stdout)
	stderr_path.write_text(process.stderr)


if __name__ == "__main__":
	pass
