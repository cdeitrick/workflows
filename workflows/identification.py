from pathlib import Path
import subprocess
from typing import List, Tuple, Dict

def groupby(iterable, callable)->Dict[str, List[Path]]:
	groups = dict()
	for element in iterable:
		key = callable(element)
		if key in groups:
			groups[key].append(element)
		else:
			groups[key] = [element]

	return groups




def get_pairs(filenames:List[Path])->List[Tuple[Path,Path]]:
	groups = groupby(filenames, lambda s: s.name.rpartition('_')[0])

	pairs = list(groups.values())
	return groups

class Kraken:
	def __init__(self, path: Path, output_folder:Path):
		path = Path(path)
		output_folder = Path(output_folder)

		if path.is_dir():
			filenames  = [f for f in path.glob("**/*") if f.suffix == '.gz']
		else:
			filenames = [path]

		pairs = get_pairs(filenames)

		for index, sample in enumerate(pairs):
			print("{} of {}".format(index, len(filenames)))
			print(sample)
			left, right = sample
			name = left.stem
			report_name = name + ".report.txt"
			output_name = output_folder / (name + ".kraken.txt")
			error_name = output_folder / (name + ".stderr.txt")
			command = ["kraken2", "--paired", "--db", "kraken_standard_database", "--report", report_name, filename]

			process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

			output_name.write_bytes(process.stdout)
			error_name.write_bytes(process.stderr)

class Metaphlan:
	def __init__(self, path:Path, output:Path):
		path = Path(path)
		output = Path(output)

		if path.is_dir():
			filenames  = [f for f in path.glob("**/*") if f.suffix == '.gz']
		else:
			filenames = [path]

		for index, filename in enumerate(filenames):
			print("{} of {}".format(index, len(filenames)))

			command = ["metaphlan.py", filename, "--blastdb", "blastdb"]

def generate_parser():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-i", "--input",
		help = "The input file or folder",
		dest = 'input'
	)
	parser.add_argument(
		"-o", "--output",
		help = "The output folder",
		dest = "output"
	)

	return parser
if __name__ == "__main__":
	parser = generate_parser()
	args = parser.parse_args()

	Kraken(args.input, args.output)