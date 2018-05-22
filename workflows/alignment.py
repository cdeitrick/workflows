from pathlib import Path
from dataclasses import dataclass
import subprocess

mummer_path = Path("/opt") / "mummer" / "MUMmer4.0" / "bin"
nucmer_path = mummer_path / "nucmer"


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


@dataclass
class AbacasOutput:
	aligned_query: Path


class Abacas:
	"""
		Uses mummer to align genomes to a reference.
		Website
		-------
		http://abacas.sourceforge.net/index.html
		Requires
		--------
		mummer

		Parameters
		----------


	"""

	abacas_path = Path("/opt") / "abacas" / "abacas.1.3.1.pl"

	def __init__(self, reference: Path, query: Path, **kwargs):
		output_folder = kwargs.get("output_folder")
		if not output_folder:
			parent_folder = kwargs['parent_folder']
			output_folder = checkdir(parent_folder / "abacas_output")
		prefix = output_folder / query.stem

		stdout_path = output_folder / "abacas_stdout.txt"
		stderr_path = output_folder / "abacas_stderr.txt"
		command_path = output_folder / "abacas_command.txt"

		command = ["perl", self.abacas_path, '-r', reference, "-q", query, "-o", prefix, '-p',
				   "nucmer"]  # "-p", nucmer_path,

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")
		command_path.write_text(' '.join(map(str, command)))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)

	@classmethod
	def from_spades(cls, spades_output):
		pass


if __name__ == "__main__":
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano"  # "Achromobacter_Valvano"

	reference = base_folder / "prokka_output" / "9271_AC036_1_trimmed" / "9271_AC036_1_trimmed.ffn"
	query = base_folder / "prokka_output" / "9272_AC036CR-0_1_trimmed" / "9272_AC036CR-0_1_trimmed.ffn"

	Abacas(reference = reference, query = query, parent_folder = base_folder)
