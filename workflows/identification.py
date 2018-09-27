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
	groups = groupby(filenames, lambda s: '_'.join(s.name.split('_')[:2]))

	pairs = list(groups.values())
	return pairs

class Kraken:
	def __init__(self, path: Path, output_folder:Path):
		path = Path(path)
		output_folder = Path(output_folder)
		if not output_folder.exists():
			output_folder.mkdir()

		if path.is_dir():
			filenames  = [f for f in path.glob("**/*") if f.suffix == '.gz']
		else:
			filenames = [path]

		pairs = get_pairs(filenames)
		for index, sample in enumerate(pairs):
			print("{} of {}".format(index, len(pairs)))
			#print(sample)
			try:
				left = [i for i in sample if 'R1' in i][0]
				right = [i for i in sample if 'R2' in i][0]
			except ValueError:
				print("Could not parse ", sample)
				continue
			name = left.stem
			output_base = output_folder / name
			report_filename = output_base.with_suffix(".report.txt")
			output_filename = output_base.with_suffix(".kraken.txt")
			error_filename = output_base.with_suffix(".stderr.txt")

			command = ["kraken2", "--paired", "--db", "kraken_standard_database", "--report", report_filename, left, right]

			process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			output_filename.write_bytes(process.stdout)
			error_filename.write_bytes(process.stderr)

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