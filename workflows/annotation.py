import argparse
from pathlib import Path

from dataclasses import dataclass

try:
	from workflows import common
	from workflows.read_assembly import SpadesOutput
	from workflows.common import SubparserType
except ModuleNotFoundError:
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
	genus: str  # ex. burkholderia
	species: str  # ex. multivorans


def prokka(genome: Path, output_folder: Path, options: ProkkaOptions, prefix = None) -> ProkkaOutput:
	if prefix is None: prefix = genome.stem
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
		common.programs.prokka,
		"--outdir", output_folder,
		"--prefix", prefix,
		"--genus", options.genus,
		"--species", options.species,
		genome
	]

	if not output.exists():
		common.run_command("prokka", prokka_command, output_folder)
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
	from tqdm import tqdm
	base_folder = Path("/home/cld100/projects/lipuma/shovill_sample_assemblies/")
	common_assembly_folder = base_folder / "assemblies"
	if not common_assembly_folder.exists():
		common_assembly_folder.mkdir()

	with open("prokka_workflow.sh") as file1:

		for sample in list(base_folder.iterdir()):
			if sample.name == 'assembly': continue

			unannotated_contigs = [i for i in sample.iterdir() if sample.name in i.name][0] / "shovill" / "contigs.fa"
			options = ProkkaOptions(genus = 'Burkholderia', species = 'cenocepacia')
			prokka_command = [
				"prokka", "--outdir", str(sample/"prokka"), "--genus", "Burkholderia", "--species", "cenocepacia", "--prefix", sample.name, str(unannotated_contigs)
			]
			expected_output = sample / "prokka" / f"{sample.name}.fna"
			cp_command = ["cp", expected_output, str(common_assembly_folder / f"{sample.name}.fna")]
			file1.write(' '.join(prokka_command) + "\n")
			file1.write(' '.join(cp_command) + "\n")