from pathlib import Path
from typing import List, Optional

from pipelines import systemio


class BreseqOutput:
	def __init__(self, output_folder: Path):
		self.index = output_folder / "output" / "index.html"
		self.summary = output_folder / "output" / "summary.html"

	def exists(self) -> bool:
		return self.index.exists()


class Breseq:
	program = "breseq"
	def __init__(self, reference: Path, threads: int = 8, population: bool = False):
		self.reference = reference
		self.threads: int = threads
		self.population = population

	@staticmethod
	def version() -> Optional[str]:
		return systemio.check_output(["breseq", "--version"])

	def test(self):
		result = self.version()
		if result is None:
			message = "Breseq cannot be found"
			raise FileNotFoundError(message)

	def run(self, output_folder: Path, *reads) -> BreseqOutput:
		output = BreseqOutput(output_folder)
		command = self.get_command(output_folder, *reads)

		if not output.exists():
			systemio.command_runner.run(command, output_folder, threads = self.threads)
		return output

	def get_command(self, output_folder: Path, *reads) -> List[str]:
		command = [
			self.program,
			"-j", self.threads,
			"-o", output_folder,
			"-r", self.reference,
		]
		if self.population:
			command = command[:1] + ["-p"] + command[1:]
		command += list(reads)

		return systemio.format_command(command)
