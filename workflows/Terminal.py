from pathlib import Path
import subprocess
class Terminal:
	def __init__(self, command, output_folder:Path, expected_output:Path):
		prefix = ""
		stdout_path = output_folder / "{}_stdout.txt".format(prefix)
		stderr_path = output_folder / "{}_stderr.txt".format(prefix)
		command_path=output_folder / "{}_command.txt".format(prefix)

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		command_path.write_text(' '.join(map(str(command))))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)


if __name__ == "__main__":
	pass