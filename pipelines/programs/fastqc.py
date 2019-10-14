from pathlib import Path
from typing import Iterable, List

from pipelines import programio, systemio, utilities


class FastQC:
	program = "fastqc"

	def __init__(self):
		pass

	@staticmethod
	def version() -> str:
		return systemio.check_output(["fastqc", "--version"])

	def run(self, output_folder: Path, *reads) -> programio.FastQCOutput:
		utilities.checkdir(output_folder)
		command = self.get_command(output_folder, reads)
		output = self.get_output(output_folder, reads)

		if not output.exists():
			systemio.command_runner.run(command, output_folder, srun = False)
		return output

	def get_command(self, output_folder: Path, reads: Iterable[Path]) -> List[str]:
		command = [self.program, "--outdir", output_folder] + list(reads)
		return systemio.format_command(command)

	@staticmethod
	def get_output(output_folder: Path, reads: Iterable[Path]) -> programio.FastQCOutput:
		return programio.FastQCOutput(
			output_folder,
			[output_folder / (i.name.split('.')[0] + '_fastqc.html') for i in reads]
		)
