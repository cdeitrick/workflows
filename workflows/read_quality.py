from pathlib import Path
from dataclasses import dataclass
from typing import Union
import subprocess
THREADS = 16


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


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


class FastQC:
	def __init__(self, forward:Path, reverse:Path, **kwargs):
		parent_folder = kwargs['parent_folder']
		output_folder = parent_folder / "fastqc_output"

		stdout_path = output_folder / "fastqc_stdout.txt"
		stderr_path = output_folder / "fastqc_stderr.txt"
		command_path = output_folder / "fastqc_command.txt"

		fastqc_command = [
			"--outdir", output_folder,
			forward, reverse
		]

		process = subprocess.run(fastqc_command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		command_path.write_text(' '.join(map(str, fastqc_command)))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)

	@classmethod
	def from_sample(cls, sample):

		return cls(sample.forward, sample.reverse, parent_folder = sample.folder)


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

		stdout_path = output_folder / "trimmomatic_stdout.txt"
		stderr_path = output_folder / "trimmomatic_stderr.txt"
		command_path = output_folder / "trimmomatic_command.txt"

		self.options = kwargs.get("options", TrimmomaticOptions())

		forward_output = output_folder / '{}.forward.trimmed.paired.fastq'.format(prefix)
		reverse_output = output_folder / '{}.reverse.trimmed.paired.fastq'.format(prefix)
		forward_output_unpaired = output_folder / '{}.forward.trimmed.unpaired.fastq'.format(prefix)
		reverse_output_unpaired = output_folder / '{}.reverse.trimmed.unpaired.fastq'.format(prefix)
		log_file = output_folder / "{}.trimmomatic_log.txt".format(prefix)

		command = [
			"trimmomatic", "PE",
			"-threads", str(self.options.threads),
			"-phred33",
			"-trimlog", log_file,
			# "name", self.options.job_name,
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

	@classmethod
	def from_sample(cls, sample) -> 'Trimmomatic':
		return cls(sample.forward, sample.reverse, parent_folder = sample.folder, prefix = sample.name)


if __name__ == "__main__":
	pass
