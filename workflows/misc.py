from pathlib import Path
import subprocess
if __name__ == "__main__":
	path = Path("/home/cld100/projects/lipuma/samples")

	compressed_files = list(path.glob("**/*.gz"))
	for index, compressed_file in enumerate(compressed_files):
		print(f"{index} of {len(compressed_files)}: {compressed_file.name}")
		command = ["tar","-C", compressed_file.parent, "-zxvf", compressed_file]
		subprocess.run(command)