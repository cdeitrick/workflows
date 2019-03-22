from pathlib import Path

import common
import sampleio


def metaphlan(forward: Path, reverse: Path, output_folder: Path):
	command = ["metaphlan2.py", forward, reverse, "--input_type", "multifastq", "-o", output_folder]
	common.run_command("metaphlan", command, output_folder)


def generate_parser():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-i", "--input",
		help = "The input folder",
		dest = 'input',
		type = Path
	)
	parser.add_argument(
		"-o", "--output",
		help = "The output folder",
		dest = "output",
		type = Path
	)

	return parser


if __name__ == "__main__":
	args = generate_parser().parse_args()
	output_folder = args.output
	output_folder = sampleio.checkdir(output_folder)
	inputio = args.input
	if inputio.suffix == '.tsv':
		samples = sampleio.read_sample_list(inputio)
	else:
		raise ValueError(f"Cannot read {inputio}")

	for sample in samples:
		print(sample)
		forward = sample.forward
		reverse = sample.reverse

		sample_output_folder = sampleio.checkdir(output_folder / sample.name)

		metaphlan(forward, reverse, sample_output_folder)
