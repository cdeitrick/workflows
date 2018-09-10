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
	program_location = Path("/home/cld100/breseq-0.33.1/bin/breseq")
	def __init__(self, reference: Path, *reads, **kwargs):
		breseq_threads = kwargs.get('threads')
		prefix = reads[0].stem
		output_folder = common.get_output_folder("breseq", **kwargs)

		output_folder = output_folder / prefix

		command = [
					  self.program_location,
					  # "-j", THREADS,
					  "-o", output_folder,
					  "-r", reference
				  ] + list(reads)

		self.output = BreseqOutput(
			output_folder,
			output_folder / "index.html"
		)

		if not self.output.exists():
			if breseq_threads:
				breseq_threads = ("-j", breseq_threads)
			self.process = common.run_command("breseq", command, output_folder, threads = breseq_threads)

	@classmethod
	def from_trimmomatic(cls, reference: Path, sample, **kwargs):
		fwd = sample.forward
		rev = sample.reverse
		ufwd = sample.forward_unpaired
		urev = sample.reverse_unpaired

		parent_folder = fwd.parent.parent
		if 'parent_folder' not in kwargs:
			kwargs['parent_folder'] = parent_folder
		# Don't use the unpaired reverse read (forward should be fine). It is generally very low quality.
		return cls(reference, fwd, rev, ufwd, **kwargs)

	@classmethod
	def from_sample(cls, reference: Path, sample, **kwargs):
		parent_folder = sample.folder
		if 'parent_folder' not in kwargs:
			kwargs['parent_folder'] = parent_folder
		return cls(reference, sample.forward, sample.reverse, **kwargs)

	@classmethod
	def from_list(cls, reference, reads, **kwargs):
		kwargs['parent_folder'] = kwargs.get('parent_folder', reads[0].parent.parent)
		return cls(reference, *reads, **kwargs)


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
