import os
import subprocess
if __name__ == "__main__":
	path = "/home/cld100/projects/lipuma/samples"
	folders = list(os.listdir(path))
	for index, folder in enumerate(folders):
		folder = path + '/' + folder
		fastqs = [folder + '/' + i for i in os.listdir(folder) if 'R1' in os.path.basename(i) or 'R2' in os.path.basename(i)]

		cat_command = ["cat"] + fastqs
		print(index, len(folders), fastqs)
		prefix = folder + '/' + os.path.basename(folder)
		mcommand = ["metaphlan2.py", "--input_type", "multifastq", "--bowtie2out", prefix + ".bt2out.txt", "-o", prefix + ".metaphlan.txt"]
		command = " ".join(cat_command) + " | " + " ".join(mcommand)
		print(command)
		os.system(command)
		#process = subprocess.run(cat_command, stdout = subprocess.PIPE, shell = True)

		#subprocess.run(command, stdin = process.stdout)
