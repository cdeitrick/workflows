from pathlib import Path
from typing import List, Optional, Union

from pipelines import systemio

ADAPTERS_FILENAME = Path(__file__).parent / "resources" / "adapters.fa"


class TrimmomaticOutput:

	# def __init__(self, output_folder: Path, prefix: Union[str, Path]):
	def __init__(self, name: str, forward: Path, reverse: Path, unpaired_forward: Optional[Path] = None, unpaired_reverse: Optional[Path] = None):
		self.name = name
		self.forward = forward
		self.reverse = reverse
		self.unpaired_forward = unpaired_forward
		self.unpaired_reverse = unpaired_reverse

	def reads(self) -> List[Path]:
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

	@classmethod
	def from_folder(cls, folder: Path, prefix: Union[str, Path]) -> 'TrimmomaticOutput':
		if isinstance(prefix, Path):
			prefix = cls.get_name_from_file(prefix)
		files = list(i for i in folder.iterdir() if i.suffix == '.fastq')
		forward = [i for i in files if ('forward' in i.name and 'unpaired' not in i.name)][0]
		reverse = [i for i in files if ('reverse' in i.name and 'unpaired' not in i.name)][0]

		try:
			unpaired_forward = [i for i in files if ('forward' in i.name and 'unpaired' in i.name)][0]
		except IndexError:
			unpaired_forward = None

		try:
			unpaired_reverse = [i for i in files if ('reverse' in i.name and 'unpaired' in i.name)][0]
		except IndexError:
			unpaired_reverse = None

		return cls(prefix, forward, reverse, unpaired_forward, unpaired_reverse)

	@classmethod
	def get_expected(cls, folder:Path, prefix:Union[str,Path])->'TrimmomaticOutput':
		if isinstance(prefix, Path): prefix = TrimmomaticOutput.get_name_from_file(prefix)
		forward: Path = folder / '{}.forward.trimmed.paired.fastq'.format(prefix)
		reverse: Path = folder / '{}.reverse.trimmed.paired.fastq'.format(prefix)
		unpaired_forward: Optional[Path] = folder / '{}.forward.trimmed.unpaired.fastq'.format(prefix)
		unpaired_reverse: Optional[Path] = folder / '{}.reverse.trimmed.unpaired.fastq'.format(prefix)
		return cls(prefix, forward, reverse, unpaired_forward, unpaired_reverse)



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

	@staticmethod
	def version() -> Optional[str]:
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
		if not output_folder.exists():
			output_folder.mkdir()

		output = TrimmomaticOutput.get_expected(output_folder, sample_name if sample_name else forward)
		command = self.get_command(forward, reverse, output)

		if not output.exists():
			systemio.command_runner.run(command, output_folder, threads = self.threads)
		return output

	def get_command(self, forward: Path, reverse: Path, output: TrimmomaticOutput) -> List[str]:
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
