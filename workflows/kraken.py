from pathlib import Path
import subprocess


class Kraken:
	def __init__(self, path: Path, output_folder:Path):
		path = Path(path)

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

if __name__ == "__main__":
	pass