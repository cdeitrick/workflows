import subprocess
from pathlib import Path

if __name__ == "__main__":
	folder = Path(__file__).parent
	reference = folder / "p148_reference_sketch.msh"
	output_file = folder / "mash_table_pairwise.txt"

	for reference in folder.iterdir():
		if reference.suffix != '.fna': continue
		for filename in folder.iterdir():
			if filename.suffix != '.fna': continue
			print("Running mash on {} and {}".format(reference, filename))
			command = [
				"mash",
				"dist",
				reference,
				filename
			]

			process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = "UTF-8")

			with output_file.open('a') as file1:
				file1.write(process.stdout)
