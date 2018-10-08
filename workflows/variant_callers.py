import argparse
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


@dataclass
class BreseqOptions:
	forward: Path
	reverse: Path
	unpaired_forward: Path
	output_folder: Path
	reference: Path
	threads: int


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

	def __init__(self, options: BreseqOptions):
		output_folder = options.output_folder
		reads = [options.forward, options.reverse]
		if options.unpaired_forward:
			reads.append(options.unpaired_forward)

		command = [
			self.program_location,
			# "-j", THREADS,
			"-o", options.output_folder,
			"-r", options.reference
		]

		command += reads

		self.output = BreseqOutput(
			output_folder,
			output_folder / "index.html"
		)

		if not self.output.exists():
			breseq_threads = ("-j", options.threads)
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


def get_commandline_parser(subparser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
	if subparser:
		parser = subparser.add_parser("breseq")
	else:
		parser = argparse.ArgumentParser("breseq")

	parser.add_argument(
		"-f", "--forward",
		help = "The forward reads",
		dest = "forward"
	)
	parser.add_argument(
		"-r", "--reverse",
		help = "The reverse reads",
		dest = "reverse"
	)
	parser.add_argument(
		"-uf", "--unpaired-forward",
		help = "The unpaired forward reads",
		dest = "unpaired_forward"
	)
	parser.add_argument(
		"-o", "--output",
		help = "The output folder",
		dest = "output_folder"
	)
	parser.add_argument(
		"--reference",
		help = "The reference sequence, preferably in .gff format.",
		dest = "reference"
	)
	parser.add_argument(
		"-t", "--threads",
		help = "The number of threads to use.",
		dest = 8
	)
	return parser


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
