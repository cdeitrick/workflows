from pathlib import Path
from typing import List, Union

from dataclasses import dataclass

try:
	from . import common
except:
	import sys

	sys.path.append(str(Path(__file__).parent))
	import common

import argparse

THREADS = 16


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


@dataclass
class FastQCOutput:
	folder: Path
	reports: List[Path]
	def exists(self):
		return all(i.exists() for i in self.reports)


class FastQC:
	def __init__(self, *reads, **kwargs):
		output_folder = common.get_output_folder("fastqc", **kwargs)

		self.fastqc_command = [
			"fastqc",
			"--outdir", output_folder
		] + list(reads)

		self.output = FastQCOutput(
			output_folder,
			[output_folder / (i.name+'.html') for i in reads]
		)

		if not self.output.exists():
			self.process = common.run_command("fastqc", self.fastqc_command, output_folder)

	@classmethod
	def from_sample(cls, sample):
		return cls(sample.forward, sample.reverse, parent_folder = sample.folder)

	@classmethod
	def from_trimmomatic(cls, sample: TrimmomaticOutput):
		reads = [sample.forward, sample.reverse, sample.forward_unpaired, sample.reverse_unpaired]
		return cls(*reads, output_folder = common.checkdir(sample.forward.parent.parent / "fastqc_trimmomatic"))


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
		self.output_folder = common.get_output_folder("trimmomatic", **kwargs)

		self.options = kwargs.get("options", TrimmomaticOptions())

		forward_output = self.output_folder / '{}.forward.trimmed.paired.fastq'.format(prefix)
		reverse_output = self.output_folder / '{}.reverse.trimmed.paired.fastq'.format(prefix)
		forward_output_unpaired = self.output_folder / '{}.forward.trimmed.unpaired.fastq'.format(prefix)
		reverse_output_unpaired = self.output_folder / '{}.reverse.trimmed.unpaired.fastq'.format(prefix)
		log_file = self.output_folder / "{}.trimmomatic_log.txt".format(prefix)
		self.output = TrimmomaticOutput(
			forward_output,
			reverse_output,
			forward_output_unpaired,
			reverse_output_unpaired
		)
		self.command = [
			"trimmomatic", "PE",
			# "-threads", str(self.options.threads),
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
		if not self.output.exists():
			self.process = common.run_command("trimmomatic", self.command, self.output_folder)

	@classmethod
	def from_sample(cls, sample) -> 'Trimmomatic':
		return cls(sample.forward, sample.reverse, parent_folder = sample.folder, prefix = sample.name)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description = "Read pre-processing."

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
		"-p", "--parent-folder",
		action = 'store',
		help = "Path to the output folder.",
		dest = 'parent_folder'
	)
	args = parser.parse_args()

	sample = common.Sample(
		name = "name",
		forward = args.forward,
		reverse = args.reverse,
		folder = args.parent_folder
	)

	FastQC.from_sample(sample)
	Trimmomatic.from_sample(sample)
