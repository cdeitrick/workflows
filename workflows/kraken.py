from pathlib import Path
import subprocess


class Kraken:
	def __init__(self, path: Path, output_folder:Path):
		path = Path(path)
		output_folder = Path(output_folder)

		if path.is_dir():
			filenames  = [f for f in path.glob("**/*") if f.suffix == '.gz']
		else:
			filenames = [path]

		for filename in filenames:
			name = filename.stem
			report_name = name + ".report.txt"
			output_name = output_folder / (name + ".kraken.txt")
			error_name = output_folder / (name + ".stderr.txt")
			command = ["kraken2", "--db", "kraken_standard_database", "--report", report_name, filename]

			process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

			output_name.write_bytes(process.stdout)
			error_name.write_bytes(process.stderr)

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