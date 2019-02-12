from pathlib import Path
import subprocess
if __name__ == "__main__":
	path = Path("/home/cld100/projects/lipuma/samples")
	folders = list(path.iterdir())
	for index, folder in enumerate(folders):
		fastqs = [i for i in folder.iterdir() if 'R1' in i.name or 'R2' in i.name]

		cat_command = ["cat"] + fastqs
		print(f"{index} of {len(folders)}: ", " ".join(map(str,cat_command)))
		command = ["metaphlan2.py", "--input_type", "multifastq", "--bowtie2output", f"{folder}/{folder.name}.bt2out.txt", "-o", f"{folder}/{folder.name}.metaphlan.txt"]

		process = subprocess.run(cat_command, stdout = subprocess.PIPE)

		subprocess.run(command, stdin = process.stdout)