import argparse
from pathlib import Path

from dataclasses import dataclass

try:
	from .read_quality import TrimmomaticOutput
	from .common import checkdir, SubparserType
	from . import common
except ModuleNotFoundError:
	from read_quality import TrimmomaticOutput
	import common


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

@dataclass
class SpadesOutput:
	output_folder: Path  # Folder where all spades output should be.
	contigs: Path
	assembly_graph: Path


	def exists(self):
		return self.contigs.exists()


def spades(forward_read: Path, reverse_read: Path, unpaired_forward_read: Path, output_folder, options: SpadesOptions) -> SpadesOutput:
	"""
		Assembles a genome via spades.
	Parameters
	----------
	forward_read: Path
	reverse_read: Path
	unpaired_forward_read: Path
	output_folder: Path
	options: SpadesOptions

	Returns
	-------
	SpadesOutput
	"""

	output = SpadesOutput(
		output_folder = output_folder,
		contigs = output_folder / "contigs.fasta",
		assembly_graph = output_folder / "assembly_graph.fastg"
	)

	command = [
		common.programs.spades,
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


def bandage(assembly_graph: Path, output_folder: Path) -> BandageOutput:

	info_command = [
		common.programs.bandage,
		"info", assembly_graph
	]
	image_command = [
		common.programs.bandage,
		"image", assembly_graph, assembly_graph.with_suffix('.fastg.png')
	]
	common.run_command('bandageinfo', info_command, output_folder)
	common.run_command('bandageimage', image_command, output_folder)
	output = BandageOutput()
	return output


def workflow(forward_read: Path, reverse_read: Path, unpaired_forward_read: Path, parent_folder: Path, options: SpadesOptions) -> SpadesOutput:
	spades_folder = parent_folder / "spades"
	bandage_folder = parent_folder / "bandage"
	spades_output = spades(forward_read, reverse_read, unpaired_forward_read, spades_folder, options)

	bandage(spades_output.assembly_graph, bandage_folder)

	return spades_output


def get_commandline_parser(subparser: SubparserType = None) -> argparse.ArgumentParser:
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
	pass
