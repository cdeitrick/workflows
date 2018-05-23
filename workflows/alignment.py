from pathlib import Path
from dataclasses import dataclass

try:
	from . import common
except:
	import common

mummer_path = Path("/opt") / "mummer" / "MUMmer4.0" / "bin"
nucmer_path = mummer_path / "nucmer"


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
		output_folder = common.get_output_folder("abacas", **kwargs)
		prefix = output_folder / query.stem

		command = ["perl", self.abacas_path, '-r', reference, "-q", query, "-o", prefix, '-p',
				   "nucmer"]  # "-p", nucmer_path,

		self.process = common.run_command("abacas", command, output_folder)

	@classmethod
	def from_spades(cls, spades_output):
		pass


if __name__ == "__main__":
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano"  # "Achromobacter_Valvano"

	reference = base_folder / "prokka_output" / "9271_AC036_1_trimmed" / "9271_AC036_1_trimmed.ffn"
	query = base_folder / "prokka_output" / "9272_AC036CR-0_1_trimmed" / "9272_AC036CR-0_1_trimmed.ffn"

	Abacas(reference = reference, query = query, parent_folder = base_folder)
