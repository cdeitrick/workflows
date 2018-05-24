from pathlib import Path

from dataclasses import dataclass

try:
	from . import common
except:
	import common


@dataclass
class BreseqOutput:
	folder: Path
	index: Path

	def exists(self):
		return self.index.exists()


class Breseq:
	"""
	Parameters
	----------
	reference:Path
		Reference file in fasta format.
	*reads: Tuple[Path]
		The reads for the sample being mapped.

	Usage
	-----

	"""

	def __init__(self, reference: Path, *reads, **kwargs):
		prefix = reads[0].stem
		output_folder = common.get_output_folder("breseq", **kwargs)

		output_folder = output_folder / prefix

		command = [
			"breseq",
			#"-j", THREADS,
			"-o", output_folder,
			"-r", reference
		] + list(reads)

		self.output = BreseqOutput(
			output_folder,
			output_folder / "index.html"
		)

		if not self.output.exists():
			self.process = common.run_command("breseq", command, output_folder)



	@classmethod
	def from_trimmomatic(cls, reference: Path, sample):
		fwd = sample.forward
		rev = sample.reverse
		ufwd = sample.forward_unpaired
		urev = sample.reverse_unpaired

		parent_folder = fwd.parent.parent

		return cls(reference, fwd, rev, ufwd, urev, parent_folder = parent_folder)

	@classmethod
	def from_list(cls, reference, reads):
		return cls(reference, *reads)


if __name__ == "__main__":
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano"
	reference = base_folder / "prokka_output" / "9271_AC036_1_trimmed" / "9271_AC036_1_trimmed.gff"
	reads_1 = [
		base_folder / "Achromobacter-Valvano" / "9271_AC036_1_trimmed.fastq",
		base_folder / "Achromobacter-Valvano" / "9271_AC036_2_trimmed.fastq",
		# base_folder / "Achromobacter-Valvano" / "9271_AC036_U1_trimmed.fastq",
		# base_folder / "Achromobacter-Valvano" / "9271_AC036_U2_trimmed.fastq"
	]

	reads_2 = [
		base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_1_trimmed.fastq",
		base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_2_trimmed.fastq",
		# base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_U1_trimmed.fastq",
		# base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_U2_trimmed.fastq"
	]

	Breseq(reference, *reads_1, parent_folder = base_folder)
	Breseq(reference, *reads_2, parent_folder = base_folder)
