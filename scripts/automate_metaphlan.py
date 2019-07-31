from pathlib import Path
from typing import Any, List

from ..pipelines import sampleio


def collect_samples(folder: Path):
	return sampleio.get_samples_from_folder(folder)


def run_metaphlan(samples: List[sampleio.SampleReads], output_folder: Path, bash: Path = None):
	"""
		Runs metaphlan over a series of samples.
	Parameters
	----------
	samples
	output_folder: Where to save the output
	bash:Path Will write the command to this file
	"""

	commands: List[List[Any]] = list()
	for sample in samples:
		command = ["metaphlan2.py", "--input_type", "fastq", "-o", output_folder, sample.forward]

		commands.append(command)

	with bash.open('w') as file1:
		for command in commands:
			string_command = " ".join([str(i) for i in command])
			file1.write(string_command + '\n\n')


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument(
		"source",
		help = "Folder containing subfolders with each sample's fastq files.",
		type = Path
	)

	parser.add_argument(
		"destination",
		help = "Where to save the files to.",
		type = Path
	)

	parser.add_argument(
		"bash",
		help = "The commands will be saved to this bash file.",
		type = Path,
		default = None
	)

	args = parser.parse_args()

	samples = collect_samples(args.source)

	run_metaphlan(samples, args.destination, args.bash)
