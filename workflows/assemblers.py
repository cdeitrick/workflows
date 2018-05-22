from pathlib import Path
from dataclasses import dataclass
import subprocess
from .read_quality import TrimmomaticOutput
from .Terminal import Workflow
THREADS = 16


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


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
		output_folder = kwargs.get("output_folder")
		if not output_folder:
			parent_folder = kwargs['parent_folder']
			output_folder = checkdir(parent_folder / "spades_output")

		spades_command_path = output_folder / "spades_command.txt"
		spades_stdout_path = output_folder / "spades_stdout.txt"
		spades_stderr_path = output_folder / "spades_stderr.txt"

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
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano" / "Achromobacter-Valvano"
	ref = TrimmomaticOutput(
		base_folder / "9271_AC036_1_trimmed.fastq",
		base_folder / "9271_AC036_2_trimmed.fastq",
		base_folder / "9271_AC036_U1_trimmed.fastq",
		base_folder / "9271_AC036_U2_trimmed.fastq"
	)
	Spades.from_trimmomatic(ref)
