import argparse
from pathlib import Path

from dataclasses import dataclass

try:
	from workflows import common
except ModuleNotFoundError:
	import common


@dataclass
class BreseqOutput:
	folder: Path
	index: Path

	def exists(self):
		return self.index.exists()


@dataclass
class BreseqOptions:
	threads: int = 8
	program:str = "breseq"

def breseq(forward:Path, reverse:Path, uforward:Path, output_folder:Path, reference:Path, options:BreseqOptions = None)->BreseqOutput:
	if options is None:
		options = BreseqOptions()
	command = [
		options.program,
		# "-j", THREADS,
		"-p",
		"-o", output_folder,
		"-r", reference,
	]

	command += [forward, reverse, uforward]

	output = BreseqOutput(
		output_folder,
		output_folder / "index.html"
	)

	if not output.exists():
		breseq_threads = ("-j", options.threads)
		common.run_command("breseq", command, output_folder, threads = breseq_threads)
	return output


def get_commandline_parser(subparser: common.SubparserType = None) -> argparse.ArgumentParser:
	if subparser:
		parser = subparser.add_parser("breseq")
	else:
		parser = argparse.ArgumentParser("breseq")

	parser.add_argument(
		"-f", "--forward",
		help = "The forward reads",
		dest = "forward"
	)
	parser.add_argument(
		"-r", "--reverse",
		help = "The reverse reads",
		dest = "reverse"
	)
	parser.add_argument(
		"-uf", "--unpaired-forward",
		help = "The unpaired forward reads",
		dest = "unpaired_forward"
	)
	parser.add_argument(
		"-o", "--output",
		help = "The output folder",
		dest = "output_folder"
	)
	parser.add_argument(
		"--reference",
		help = "The reference sequence, preferably in .gff format.",
		dest = "reference"
	)
	parser.add_argument(
		"-t", "--threads",
		help = "The number of threads to use.",
		dest = 8
	)
	return parser


if __name__ == "__main__":
	pass