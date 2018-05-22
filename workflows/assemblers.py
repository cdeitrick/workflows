from pathlib import Path
from dataclasses import dataclass
import subprocess
from typing import Union

THREADS = 16


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


@dataclass
class SpadesOutput:
	output_contigs: Path
	output_graph: Path


@dataclass
class TrimmomaticOutput:
	forward: Path
	reverse: Path
	forward_unpaired: Path
	reverse_unpaired: Path

	def exists(self):
		f = self.forward.exists()
		r = self.reverse.exists()
		fu = self.forward_unpaired.exists()
		ru = self.reverse_unpaired.exists()

		return f and r and fu and ru


@dataclass
class TrimmomaticOptions:
	leading: int = 20
	trailing: int = 20
	window: str = "4:20"
	minimum_length: int = 70
	clip: Union[str, Path] = Path("/opt/trimmomatic/Trimmomatic-0.36/adapters/NexteraPE-PE.fa")
	job_name: str = "trimmomatic"
	threads: int = THREADS

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
			parent_folder = checkdir(parent_folder / "spades_output")
			output_folder = checkdir(parent_folder / "{}_spades_output".format(forward.stem))

		spades_command_path = output_folder / "spades_command.txt"
		spades_stdout_path = output_folder / "spades_stdout.txt"
		spades_stderr_path = output_folder / "spades_stderr.txt"

		command = [
			"spades.py",
			"-t", str(THREADS),
			"--careful",
			#21,33,55,77,91
			"-k", '21,33,55,77'#"15,21,25,31", #Must be odd values
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


class Trimmomatic:
	"""
		Parameters
		----------
		forward, reverse:Path
			The reads to trim.
		prefix: str
			prefix of the resulting files.
		Attributes
		----------
		output: TrimmomaticOutput
			Contains the locations of the relevant output files.
		Usage
		-----
		Trimmomatic(forward_read, reverse_read, parent_folder = parent_folder)
		output:
		parent_folder
			trimmomatic_output
				forward_trimmed_read
				reverse_trimmed_read
				forward_unparied_trimmed_read
				reverse_unpaired_trimmed_read
				trimmomatic_command.text
				trimmomatic_stderr.txt
				trimmomatic_stdout.txt
	"""
	def __init__(self, forward: Path, reverse: Path, **kwargs):
		prefix = kwargs.get('prefix', forward.stem)
		output_folder = kwargs.get("output_folder")
		if not output_folder:
			parent_folder = checkdir(kwargs['parent_folder'])
			output_folder = checkdir(parent_folder / "trimmomatic_output")

		#prefix = checkdir(output_folder / kwargs.get('prefix', forward.stem))


		stdout_path = output_folder / "trimmomatic_stdout.txt"
		stderr_path = output_folder / "trimmomatic_stderr.txt"
		command_path = output_folder / "trimmomatic_command.txt"

		self.options = kwargs.get("options", TrimmomaticOptions())

		forward_output = output_folder / '{}.trimmed.paired.fastq'.format(prefix)
		reverse_output = output_folder / '{}.trimmed.paired.fastq'.format(prefix)
		forward_output_unpaired = output_folder / '{}.trimmed.unpaired.fastq'.format(prefix)
		reverse_output_unpaired = output_folder / '{}.trimmed.unpaired.fastq'.format(prefix)
		log_file = output_folder / "{}.trimmomatic_log.txt".format(prefix)

		command = [
			"trimmomatic", "PE",
			"-threads", str(self.options.threads),
			"-phred33",
			"-trimlog", log_file,
			#"name", self.options.job_name,
			forward,
			reverse,
			forward_output, forward_output_unpaired,
			reverse_output, reverse_output_unpaired,
			"ILLUMINACLIP:{}:2:30:10".format(self.options.clip),
			"LEADING:{}".format(self.options.leading),
			"TRAILING:{}".format(self.options.trailing),
			"SLIDINGWINDOW:{}".format(self.options.window),
			"MINLEN:{}".format(self.options.minimum_length)
		]

		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		command_path.write_text(' '.join(map(str, command)))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)

		self.output = TrimmomaticOutput(
			forward_output,
			reverse_output,
			forward_output_unpaired,
			reverse_output_unpaired
		)

		print("Trimomatic Output Exists: ", self.output.exists())

	@classmethod
	def from_sample(cls, output_folder:Path, sample)->'Trimmomatic':
		return cls(sample.forward, sample.reverse, parent_folder = output_folder, prefix = sample.name)

if __name__ == "__main__":
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano" / "Achromobacter-Valvano"
	ref = TrimmomaticOutput(
		base_folder,
		base_folder / "9271_AC036_1_trimmed.fastq",
		base_folder / "9271_AC036_2_trimmed.fastq",
		base_folder / "9271_AC036_U1_trimmed.fastq",
		base_folder / "9271_AC036_U2_trimmed.fastq"
	)
	Spades.from_trimmomatic(ref)
