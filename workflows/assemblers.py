from pathlib import Path
from dataclasses import dataclass
import subprocess




import argparse

try:
	from .read_quality import TrimmomaticOutput
	from .Terminal import Workflow
	from .common import checkdir
except:
	import read_quality.TrimmomaticOutput as TrimmomaticOutput
	import Terminal.Workflow as Workflow
	import common.checkdir as checkdir

THREADS = 16


@dataclass
class SpadesOutput:
	output_folder:Path # Folder where all spades output should be.
	output_contigs: Path
	output_graph: Path

	def exists(self):
		return self.output_contigs.exists()


class Spades:
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

		output_folder = kwargs.get("output_folder")
		if not output_folder:
			parent_folder = kwargs['parent_folder']
			output_folder = checkdir(parent_folder / "spades_output")

		spades_command_path = output_folder / "spades_command.txt"
		spades_stdout_path = output_folder / "spades_stdout.txt"
		spades_stderr_path = output_folder / "spades_stderr.txt"

		command = [
			spades_program,
			"-t", str(THREADS),
			"--careful",
			"-k", spades_kmer_length,  # "15,21,25,31", #Must be odd values and less than 128
			"--pe1-1", forward,
			"--pe1-2", reverse,
			"--pe1-s", forward_unpaired,
			"--pe1-s", reverse_unpaired,
			"-o", output_folder
		]

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		spades_command_path.write_text(' '.join(map(str, command)))
		spades_stdout_path.write_text(process.stdout)
		spades_stderr_path.write_text(process.stderr)

		self.output = SpadesOutput(
			output_folder = output_folder,
			output_contigs = output_folder / "contigs.fasta",
			output_graph = output_folder / "assembly_graph.fastg"
		)

	@classmethod
	def from_trimmomatic(cls, sample: TrimmomaticOutput, **kwargs):
		fwd = sample.forward
		rev = sample.reverse
		ufwd = sample.forward_unpaired
		urev = sample.reverse_unpaired

		kwargs['parent_folder'] = kwargs.get('parent_folder', fwd.parent.parent)

		return cls(fwd, rev, ufwd, urev, **kwargs)

class SpadesWorkflow:
	def __init__(self, forward: Path, reverse: Path, forward_unpaired: Path, reverse_unpaired: Path, **kwargs):
		output_folder = kwargs['parent_folder'] / "spades_output"

		command = [
			"spades.py",
			"-t", str(THREADS),
			"--careful",
			# 21,33,55,77,91
			"-k", '21,33,55,71',  # "15,21,25,31", #Must be odd values
			"--pe1-1", forward,
			"--pe1-2", reverse,
			"--pe1-s", forward_unpaired,
			"--pe1-s", reverse_unpaired,
			"-o", output_folder
		]

		expected_output = SpadesOutput(
			output_folder = output_folder,
			output_contigs = output_folder / "contigs.fasta",
			output_graph = output_folder / "assembly_graph.fastg"
		)

		workflow = Workflow('spades', command, output_folder)



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

	Spades(args.forward, args.reverse, *args.unpaired, parent_folder = args.parent_folder)

