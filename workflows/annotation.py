from pathlib import Path
from dataclasses import dataclass
import argparse
import subprocess


@dataclass
class ProkkaOutput:
	gff: Path
	gbk: Path
	fna: Path
	faa: Path
	ffn: Path
	sqn: Path
	fsa: Path
	tbl: Path
	err: Path
	log: Path
	txt: Path
	tsv: Path

	def exists(self):
		return self.gff.exists()


class Prokka:
	def __init__(self, genome: Path, **kwargs):
		prefix = kwargs.get('prefix', genome.stem)
		output_folder = kwargs.get("output_folder")
		if not output_folder:
			parent_folder = kwargs['parent_folder']
			output_folder = parent_folder / "prokka_output"  # Don't make the folder

		print("Saving prokka output to ", output_folder)

		stdout_path = output_folder / "prokka_stdout.txt"
		stderr_path = output_folder / "prokka_stderr.txt"
		command_path = output_folder / "prokka_command.txt"

		prokka_command = [
			"prokka",
			"--outdir", output_folder,
			"--prefix", prefix,
			genome
		]

		prokka_process = subprocess.run(prokka_command, stdout = subprocess.PIPE, stderr = subprocess.PIPE,
										encoding = "UTF-8")
		command_path.write_text(' '.join(map(str, prokka_command)))
		stdout_path.write_text(prokka_process.stdout)
		stderr_path.write_text(prokka_process.stderr)

		basename = output_folder / prefix
		self.output = ProkkaOutput(
			gff = basename.with_suffix(".gff"),
			gbk = basename.with_suffix(".gbk"),
			fna = basename.with_suffix(".fna"),
			faa = basename.with_suffix(".faa"),
			ffn = basename.with_suffix(".ffn"),
			sqn = basename.with_suffix(".sqn"),
			fsa = basename.with_suffix(".fsa"),
			tbl = basename.with_suffix(".tbl"),
			err = basename.with_suffix(".err"),
			log = basename.with_suffix(".log"),
			txt = basename.with_suffix(".txt"),
			tsv = basename.with_suffix(".tsv")
		)

	@classmethod
	def from_spades(cls, spades_output, **kwargs):
		sample = spades_output.output_contigs
		kwargs['parent_folder'] = kwargs.get('parent_folder', sample.parent.parent)
		return cls(sample, **kwargs)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description = "Assembly annotation."

	)

	parser.add_argument(
		"-s", "--sample",
		action = 'store',
		help = "Path to the sample contigs.",
		dest = "sample"
	)
	parser.add_argument(
		"-p", "--parent-folder",
		action = "store",
		help = "Path to the parent folder.",
		dest = 'parent_folder'
	)
	args = parser.parse_args()

	Prokka(genome = args.sample, parent_folder = args.parent_folder)
