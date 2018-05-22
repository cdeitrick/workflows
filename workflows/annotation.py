from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict
import os

import subprocess


def checkdir(path):
	if isinstance(path, str): path = Path(path)
	if not path.exists(): path.mkdir()
	return path


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

	def __post_init__(self):
		data: Dict[str, Path] = asdict(self)
		is_valid = all(i.exists() for i in data.values())
		if not is_valid:
			for key, value in data.items():
				print(key, value.exists(), value)

			raise FileNotFoundError("Some of Prokka's output files are missing.")


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

		basename = output_folder / "{}_prokka".format(prefix)
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
	base_folder = Path.home() / "projects" / "Achromobacter_Valvano"

	contigs1 = base_folder / "9271_AC036_1_trimmed_spades_output" / "contigs.fasta"
	#contigs2 = base_folder / "9272_AC036CR-0_1_trimmed_spades_output" / "contigs.fasta"

	Prokka(contigs1, parent_folder = base_folder, prefix = "9271_AC036_1_trimmed")
	#Prokka(contigs2, parent_folder = base_folder, prefix = "9272_AC036CR-0_1_trimmed")
