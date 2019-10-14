from pathlib import Path
from typing import List, Optional

from loguru import logger

from pipelines import systemio, programio, utilities


class Shovill:
	program = "shovill"

	def __init__(self, minlen = 500, assembler = 'spades', threads: int = 8):
		self.minlen = minlen
		self.assembler = assembler
		self.threads = threads

	def run(self, forward: Path, reverse: Path, output_folder: Path, sample_name:Optional[str] = None) -> programio.ShovillOutput:
		if sample_name is None:
			sample_name = utilities.get_name_from_reads(forward)
		output = programio.ShovillOutput.expected(output_folder, sample_name)
		command = self.get_command(forward, reverse, output_folder)

		if not output.exists():
			logger.info(f"Assembly: Generating assembly...")
			systemio.command_runner.run(command, output_folder)
		else:
			logger.info(f"Assembly: The output files already exist in {output_folder}")

		return output

	def get_command(self, forward: Path, reverse: Path, output_folder: Path) -> List[str]:
		command = [
			self.program,
			"--minlen", self.minlen,
			"--assembler", self.assembler,
			"--outdir", output_folder,
			"--R1", forward,
			"--R2", reverse,
			"--force",  # Since the output folder is automatically generated.
			"--cpus", self.threads
		]
		return systemio.format_command(command)
