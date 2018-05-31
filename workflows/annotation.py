import argparse
from pathlib import Path

from dataclasses import dataclass
import subprocess
try:
	from . import common
except:
	import common


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

		output_folder = common.get_output_folder("prokka", make_dirs = False, **kwargs)
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

		prokka_command = [
			"prokka",
			"--outdir", output_folder,
			"--prefix", prefix,
			"--genus", "burkholderia",
			"--species", "multivorans",
			genome
		]

		if not self.output.exists():
			#subprocess.run(['module', 'load', 'prokka'])
			self.process = common.run_command("prokka", prokka_command, output_folder)
			#subprocess.run(['module', 'unload', 'prokka'])

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
