from pathlib import Path
from typing import Union, List, Optional

from pipelines import systemio

ADAPTERS_FILENAME = Path(__file__).parent / "resources" / "adapters.fa"


class TrimmomaticOutput:
	def __init__(self, output_folder: Path, prefix: Union[str, Path]):
		if isinstance(prefix, Path): prefix = self.get_name_from_file(prefix)
		self.forward: Path = output_folder / '{}.forward.trimmed.paired.fastq'.format(prefix)
		self.reverse: Path = output_folder / '{}.reverse.trimmed.paired.fastq'.format(prefix)
		self.unpaired_forward: Path = output_folder / '{}.forward.trimmed.unpaired.fastq'.format(prefix)
		self.unpaired_reverse: Path = output_folder / '{}.reverse.trimmed.unpaired.fastq'.format(prefix)
		self.log_file: Path = output_folder / "trimmomatic.log.txt"

	def reads(self)->List[Path]:
		return [self.forward, self.reverse, self.unpaired_forward, self.unpaired_reverse]
	def exists(self):
		f = self.forward.exists()
		r = self.reverse.exists()
		fu = self.unpaired_forward.exists()
		ru = self.unpaired_reverse.exists()

		return f and r and fu and ru

	@staticmethod
	def get_name_from_file(path: Path) -> str:
		name = path.stem

		# If the path refers to a read file, only the first part is usefull.
		if 'R1' in name or 'R2' in name:
			name = name.split('_')[0]
		return name


class Trimmomatic:
	"""
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
	program = "trimmomatic"
	def __init__(self, leading: int = 3, trailing: int = 3, window: str = "4:15", minimum: int = 36, clip = ADAPTERS_FILENAME, threads: int = 8):
		self.leading: int = leading
		self.trailing: int = trailing
		self.window: str = window
		self.minimum: int = minimum
		self.clip: Path = clip
		self.threads: int = threads
	@staticmethod
	def version()->Optional[str]:
		return systemio.check_output(["trimmomatic", "-version"])

	def test(self):
		result = self.version()
		if result is None:
			message = "Trimmomatic cannot be found."
			raise FileNotFoundError(message)

	def run(self, forward: Path, reverse: Path, output_folder: Path, sample_name: str = None) -> TrimmomaticOutput:
		"""
			Runs trimmomatic on the given pair of reads.
		Parameters
		----------
		forward, reverse, output_folder
		sample_name: Optional[str]
			Will form the prefix of the output files if given. Otherwise, the name of the forward read will be used to generate the output names.
		"""

		output_folder.mkdir()
		output = self.get_expected_output(output_folder, sample_name if sample_name else forward)
		command = self.get_command(forward, reverse, output)

		if not output.exists():
			systemio.command_runner.run(command, output_folder, threads = self.threads)
		return output

	@staticmethod
	def get_expected_output(output_folder: Path, sample_name: Union[Path, str]):
		output = TrimmomaticOutput(output_folder, sample_name)
		return output

	def get_command(self, forward: Path, reverse: Path, output: TrimmomaticOutput) -> List[str]:
		command = [
			self.program, "PE",
			# "-threads", str(self.options.threads),
			"-phred33",
			"-trimlog", output.log_file,
			"-threads", self.threads,
			# "name", self.options.job_name,
			forward,
			reverse,
			output.forward, output.unpaired_forward,
			output.reverse, output.unpaired_reverse,
			f"ILLUMINACLIP:{self.clip}:2:30:10",
			f"LEADING:{self.leading}",
			f"TRAILING:{self.trailing}",
			f"SLIDINGWINDOW:{self.window}",
			f"MINLEN:{self.minimum}"
		]
		return systemio.format_command(command)

