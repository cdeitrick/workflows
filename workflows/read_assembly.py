import argparse
from pathlib import Path

from dataclasses import dataclass

try:
	from .read_quality import TrimmomaticOutput
	from .common import checkdir
	from . import common
except:
	import read_quality
	import common

	TrimmomaticOutput = read_quality.TrimmomaticOutput


@dataclass
class BandageOutput:
	pass


@dataclass
class SpadesOptions:
	# output_folder: Path
	# forward: Path
	# reverse: Path
	# unpaired_forward: Path = None
	# unpaired_reverse: Path = None  # Don't use the unpaired reverse reads.
	kmers: str = '21,33,55,71'  # A comma-separated list of odd integers less than 128.
	threads: int = 16
	careful: bool = True

	@classmethod
	def from_trimmomatic(cls, sample: TrimmomaticOutput, **kwargs):
		fwd = sample.forward
		rev = sample.reverse
		ufwd = sample.forward_unpaired
		urev = sample.reverse_unpaired

		return cls(fwd, rev, ufwd, **kwargs)


@dataclass
class SpadesOutput:
	output_folder: Path  # Folder where all spades output should be.
	contigs: Path
	assembly_graph: Path

	def exists(self):
		return self.contigs.exists()


def spades(forward_read: Path, reverse_read: Path, unpaired_forward_read: Path, output_folder, options: SpadesOptions) -> SpadesOutput:
	"""
	Parameters
	----------
	forward, reverse, forward_unpaired, reverse_unpaired:Path
		The reads to assemble
	"""

	output = SpadesOutput(
		output_folder = output_folder,
		contigs = output_folder / "contigs.fasta",
		assembly_graph = output_folder / "assembly_graph.fastg"
	)

	command = [
		spades_program,
		# "-t", str(THREADS),
		"--careful",
		"-k", options.kmers,  # "15,21,25,31", #Must be odd values and less than 128
		"--pe1-1", forward_read,
		"--pe1-2", reverse_read,
		"-o", output_folder
	]
	if unpaired_forward_read:
		command += ['--pe1-s', unpaired_forward_read]

	if not output.exists():
		common.run_command("spades", command, output_folder)

	return output


def bandage(assembly_graph: Path) -> BandageOutput:
	# TODO: Implement bandage.
	bandage_program = "bandage"
	info_command = [
		bandage_program,
		"info", assembly_graph
	]
	image_command = [
		bandage_program,
		"image", assembly_graph, assembly_graph.with_suffix('.fastg.png')
	]
	output = BandageOutput()
	return output


def workflow(forward_read: Path, reverse_read: Path, unpaired_forward_read: Path, output_folder: Path, options: SpadesOptions) -> SpadesOutput:
	spades_output = spades(forward_read, reverse_read, unpaired_forward_read, output_folder, options)

	bandage_output = bandage(spades_output.assembly_graph)

	return spades_output


def get_commandline_parser(subparser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
	if subparser:
		assembly_parser = subparser.add_parser('assembly')
	else:
		assembly_parser = argparse.ArgumentParser()

	assembly_parser.add_argument(
		"-f", "--forward",
		help = "Forward Read",
		dest = "forward"
	)
	assembly_parser.add_argument(
		"-r", "--reverse",
		help = "Reverse Read",
		dest = "reverse",
	)
	assembly_parser.add_argument(
		"-uf", "--unpaired-forward",
		help = "The unpaired forward reads.",
		dest = "unpaired forward"
	)

	assembly_parser.add_argument(
		"-k", "--kmers",
		help = "A comma-separated list of the kmers to use during the assembly process.",
		dest = "kmers",
		default = "21,33,55,71"
	)
	assembly_parser.add_argument(
		"--not-careful",
		help = "Turns of careful assembly.",
		action = "store_false",
		dest = "careful"
	)
	assembly_parser.add_argument(
		"-t", "--threads",
		help = "Threads to use.",
		dest = "threads",
		default = 8
	)

	return assembly_parser


if __name__ == "__main__":
	parser = get_commandline_parser()
	args = parser.parse_args()

	SpadesWorkflow(args.forward, args.reverse, *args.unpaired, parent_folder = args.parent_folder)
