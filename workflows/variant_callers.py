from pathlib import Path
import subprocess
from dataclasses import dataclass

THREADS = "24"
@dataclass
class BreseqOutput:
	folder: Path
	index: Path


class Breseq:
	"""
	Parameters
	----------
	reference:Path
		Reference file in fasta format.
	*reads: Tuple[Path]
		The reads for the sample being mapped.

	Usage
	-----

	"""
	def __init__(self, reference: Path, *reads, **kwargs):
		prefix = reads[0].stem
		output_folder = kwargs.get("output_folder")
		if not output_folder:
			parent_folder = kwargs['parent_folder']
			output_folder = parent_folder / "breseq_output"
			if not output_folder.exists():
				output_folder.mkdir()
		output_folder = output_folder / prefix
		stdout_path = output_folder / "breseq_stdout.txt"
		stderr_path = output_folder / "breseq_stderr.txt"
		command_path = output_folder / "breseq_command.txt"

		command = ["srun","-T", THREADS, "breseq", "-j", THREADS, "-o", output_folder, "-r", reference] + list(reads)
		process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

		command_path.write_text(' '.join(map(str, command)))
		stdout_path.write_text(process.stdout)
		stderr_path.write_text(process.stderr)

		self.output = BreseqOutput(
			output_folder,
			output_folder / "index.html"
		)

	@classmethod
	def from_trimmomatic(cls, reference: Path, sample):
		fwd = sample.forward
		rev = sample.reverse
		ufwd = sample.forward_unpaired
		urev = sample.reverse_unpaired

		return cls(reference, fwd, rev, ufwd, urev)

	@classmethod
	def from_list(cls, reference, reads):
		return cls(reference, *reads)


if __name__ == "__main__":
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano"
	reference = base_folder / "prokka_output" / "9271_AC036_1_trimmed" / "9271_AC036_1_trimmed.gff"
	reads_1 = [
		base_folder / "Achromobacter-Valvano" / "9271_AC036_1_trimmed.fastq",
		base_folder / "Achromobacter-Valvano" / "9271_AC036_2_trimmed.fastq",
		#base_folder / "Achromobacter-Valvano" / "9271_AC036_U1_trimmed.fastq",
		#base_folder / "Achromobacter-Valvano" / "9271_AC036_U2_trimmed.fastq"
	]

	reads_2 = [
		base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_1_trimmed.fastq",
		base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_2_trimmed.fastq",
		#base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_U1_trimmed.fastq",
		#base_folder / "Achromobacter-Valvano" / "9272_AC036CR-0_U2_trimmed.fastq"
	]

	Breseq(reference, *reads_1, parent_folder = base_folder)
	Breseq(reference, *reads_2, parent_folder = base_folder)
