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
class SpadesOutput:
	output_folder: Path  # Folder where all spades output should be.
	output_contigs: Path
	output_graph: Path

	def exists(self):
		return self.output_contigs.exists()


class SpadesWorkflow:
	"""
	Parameters
	----------
	forward, reverse, forward_unpaired, reverse_unpaired:Path
		The reads to assemble
	parent_folder:Path
	output_folder:Path
	Usage
	-----
		Spades(fwd, rev, ufwd, rev, parent_folder = parent_folder)
		output:
			parent_folder
				spades_output
					contigs.fasta
					assembly_graph.fastg

		Spades.from_trimmomatic(trimmomatic_output, parent_folder = parent_folder)
	"""

	def __init__(self, forward: Path, reverse: Path, forward_unpaired: Path, reverse_unpaired: Path, **kwargs):
		spades_program = kwargs.get('spades', 'spades.py')
		spades_kmer_length = kwargs.get('kmers', '21,33,55,71')

		output_folder = common.get_output_folder("spades", **kwargs)

		self.output = SpadesOutput(
			output_folder = output_folder,
			output_contigs = output_folder / "contigs.fasta",
			output_graph = output_folder / "assembly_graph.fastg"
		)

		command = [
			spades_program,
			#"-t", str(THREADS),
			"--careful",
			"-k", spades_kmer_length,  # "15,21,25,31", #Must be odd values and less than 128
			"--pe1-1", forward,
			"--pe1-2", reverse,
			"--pe1-s", forward_unpaired,
			"--pe1-s", reverse_unpaired,
			"-o", output_folder
		]

		common.run_command("spades", command, output_folder)

	@classmethod
	def from_trimmomatic(cls, sample: TrimmomaticOutput, **kwargs):
		fwd = sample.forward
		rev = sample.reverse
		ufwd = sample.forward_unpaired
		urev = sample.reverse_unpaired

		kwargs['parent_folder'] = kwargs.get('parent_folder', fwd.parent.parent)

		return cls(fwd, rev, ufwd, urev, **kwargs)


class Bandage:
	def __init__(self, assembly_graph: Path):
		bandage_program = "bandage"
		info_command = [
			bandage_program,
			"info", assembly_graph
		]
		image_command = [
			bandage_program,
			"image", assembly_graph, assembly_graph.with_suffix('.fastg.png')
		]


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description = "Read assembling."

	)

	parser.add_argument(
		"-n", "--name",
		action = 'store',
		help = "Name of the sample. Used when naming the output files.",
		dest = "name"
	)
	parser.add_argument(
		"-f", "--forward",
		action = "store",
		help = "Path the the forward read.",
		dest = 'forward'
	)
	parser.add_argument(
		"-r", "--reverse",
		action = "store",
		help = "Path the the reverse read",
		dest = "reverse"
	)
	parser.add_argument(
		"-u", "--unpaired",
		action = "append",
		help = "Path(s) to the unpaired reads.",
		dest = "unpaired"
	)
	parser.add_argument(
		"-p", "--parent-folder",
		action = 'store',
		help = "Path to the output folder.",
		dest = 'parent_folder'
	)
	args = parser.parse_args()

	SpadesWorkflow(args.forward, args.reverse, *args.unpaired, parent_folder = args.parent_folder)
