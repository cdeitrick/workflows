import argparse
from pathlib import Path
from typing import Union

from dataclasses import dataclass

try:
	from . import common
	from .read_assembly import SpadesOutput
	from .common import SubparserType
except:
	import common
	from read_assembly import SpadesOutput
	from common import SubparserType


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


@dataclass
class ProkkaOptions:
	filename: Path
	output: Path  # Folder
	prefix: str
	genus: str  # ex. burkholderia
	species: str  # ex. multivorans

	@classmethod
	def from_parser(cls, parser: Union[argparse.Namespace, 'ProkkaOptions']) -> 'ProkkaOptions':
		return cls(
			filename = Path(parser.filename),
			output = Path(parser.output),
			prefix = parser.prefix,
			genus = parser.genus,
			species = parser.species
		)

	@classmethod
	def from_args(cls, io: Union[str, Path, SpadesOutput], output: Path, species: str, genus: str, prefix = None) -> 'ProkkaOptions':
		if isinstance(io, SpadesOutput):
			filename = io.contigs
		else:
			filename = Path(io)
		if prefix is None:
			prefix = filename.stem
		ofolder = Path(output)

		return cls(
			filename = filename,
			output = ofolder,
			prefix = prefix,
			genus = genus,
			species = species
		)


def prokka(genome: Path, output_folder: Path, options: ProkkaOptions, prefix = None) -> ProkkaOutput:
	basename = output_folder / prefix
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

	prokka_command = [
		"prokka",
		"--outdir", output_folder,
		"--prefix", prefix,
		"--genus", options.genus,
		"--species", options.species,
		genome
	]

	if not output.exists():
		process = common.run_command("prokka", prokka_command, output_folder)
	return output


def workflow(genome: Path, output_folder: Path, options: ProkkaOptions) -> ProkkaOutput:
	prokka_output = prokka(genome, output_folder, options)

	return prokka_output


def get_commandline_parser(subparser: SubparserType = None) -> argparse.ArgumentParser:
	if subparser:
		annotation_parser = subparser.add_parser("annotation")
	else:
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
	parser = get_commandline_parser()
	args = parser.parse_args()

	options = ProkkaOptions.from_parser(args)

	Prokka(genome = args.sample, options = options)
