from pathlib import Path
from typing import List, Optional

from loguru import logger

from pipelines import systemio, programio
from pipelines.resources import illumina_filename

ADAPTERS_FILENAME = illumina_filename


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

	def __init__(self, leading: int = 3, trailing: int = 3, window: str = "4:15", minimum: int = 36, clip = ADAPTERS_FILENAME, threads: int = 8,
			stringent: bool = False):
		self.leading: int = leading
		self.trailing: int = trailing
		self.window: str = window
		self.minimum: int = minimum
		self.clip: Path = clip
		self.threads: int = threads

		if stringent:
			self.leading = 20
			self.trailing = 20
			self.minimum = 70

	def __str__(self) -> str:
		string = f"Trimmomatic(leading = {self.leading}, trailing = {self.trailing}, minimum = {self.minimum}, clip = {self.clip.exists()})"
		return string

	@staticmethod
	def version() -> Optional[str]:
		return systemio.check_output(["trimmomatic", "-version"])

	def test(self):
		result = self.version()
		if result is None:
			message = "Trimmomatic cannot be found."
			raise FileNotFoundError(message)

		# Make sure the adapters filename exists
		if not self.clip.exists():
			message = f"Cannot locate the adaptor file: {self.clip}"
			raise FileNotFoundError(message)

	def run(self, forward: Path, reverse: Path, output_folder: Path, sample_name: str = None) -> programio.TrimmomaticOutput:
		"""
			Runs trimmomatic on the given pair of reads.
		Parameters
		----------
		forward, reverse, output_folder
		sample_name: Optional[str]
			Will form the prefix of the output files if given. Otherwise, the name of the forward read will be used to generate the output names.
		"""
		logger.info(f"Running Trimmomatic...")
		if not output_folder.exists():
			output_folder.mkdir()

		output = programio.TrimmomaticOutput.expected(output_folder, sample_name)
		command = self.get_command(forward, reverse, output)

		if not output.exists():
			systemio.command_runner.run(command, output_folder, threads = self.threads)

		return output

	def get_command(self, forward: Path, reverse: Path, output: programio.TrimmomaticOutput) -> List[str]:
		command = [
			self.program, "PE",
			# "-threads", str(self.options.threads),
			"-phred33",
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
