from pathlib import Path
from typing import List, Optional

from pipelines import systemio, utilities, programio


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

	def run(self, output_folder: Path, *reads) -> programio.BreseqOutput:
		sample_name = utilities.get_name_from_reads(reads[0])
		output = programio.BreseqOutput.expected(output_folder, sample_name)
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


