from pathlib import Path
from typing import List

from pipelines import systemio


class ShovillOutput:
	def __init__(self, output_folder: Path):
		self.contigs = output_folder / "contigs.fa"
		self.contigs_gfa = output_folder / "contigs.gfa"
		self.corrections = output_folder / "shovill.corrections"
		self.contigs_spades = output_folder / "spades.fasta"

	def exists(self) -> bool:
		return self.contigs.exists()


class Shovill:
	program = "shovill"
	def __init__(self, minlen = 500, assembler = 'spades', threads: int = 8):
		self.minlen = minlen
		self.assembler = assembler
		self.threads = threads

	def run(self, forward: Path, reverse: Path, output_folder: Path) -> ShovillOutput:
		output = self.get_output(output_folder)
		command = self.get_command(forward, reverse, output_folder)

		if not output.exists():
			systemio.command_runner.run(command, output_folder)

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
	@staticmethod
	def get_output(output_folder: Path) -> ShovillOutput:
		return ShovillOutput(output_folder)
