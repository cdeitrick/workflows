import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from loguru import logger

from pipelines import systemio


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

	def __init__(self, genus: str, species: str):
		self.genus = genus
		self.species = species
		# Test if the program exists
		self.location = self.get_install()

	@staticmethod
	def get_install()->Optional[Path]:
		#Try to locate the file using `which`
		command = ["which", "prokka"]
		result = systemio.check_output(command)

		if result is None:
			# Assume prokka is part of anaconda
			result = systemio.get_anaconda_install() / "prokka"
			result = result if result.exists() else None

		return result

	def version(self):
		command = [self.get_install(), "--version"]
		result = systemio.check_output(command)
		return result

	def run(self, assembly: Path, output_folder: Path) -> ProkkaOutput:
		output = self.get_output(assembly, output_folder)
		command = self.get_command(assembly, output_folder)

		if not output.exists():
			systemio.run_command("prokka", command, output_folder)
		return output

	def get_command(self, assembly: Path, output_folder: Path) -> List[str]:
		prokka_command = [
			systemio.programs.prokka,
			"--outdir", output_folder,
			"--prefix", assembly.stem,
			"--genus", self.genus,
			"--species", self.species,
			assembly
		]
		return prokka_command

	@staticmethod
	def get_output(assembly: Path, output_folder: Path) -> ProkkaOutput:
		basename = output_folder / assembly.stem
		output = ProkkaOutput(
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
		return output


def create_parser() -> argparse.ArgumentParser:
	annotation_parser = argparse.ArgumentParser()
	annotation_parser.add_argument(
		'--input',
		help = 'The sequence to annotate',
		dest = 'filename'
	)
	annotation_parser.add_argument(
		'--output',
		help = "The output folder or filename",
		dest = 'output'
	)
	annotation_parser.add_argument(
		'--prefix',
		help = "The output filename prefix.",
		dest = 'prefix'
	)

	annotation_parser.add_argument(
		"--genus",
		help = "The closes genus to the sequence.",
		dest = 'genus'
	)
	annotation_parser.add_argument(
		"--species",
		help = 'The species closes to the sequences.',
		dest = 'species'
	)
	return annotation_parser


if __name__ == "__main__":
	pass
