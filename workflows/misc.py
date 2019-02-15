import os
import subprocess
if __name__ == "__main__":
	path = "/home/cld100/projects/lipuma/samples"
	folders = list(i for i in os.listdir(path) if os.path.isdir(i))
	for index, folder in enumerate(folders):
		folder = path + '/' + folder
		fastqs = [folder + '/' + i for i in os.listdir(folder) if 'R1' in os.path.basename(i) or 'R2' in os.path.basename(i)]

		cat_command = ["cat"] + fastqs
		print(index, len(folders), fastqs)
		prefix = folder + '/' + os.path.basename(folder)
		expected_output = prefix + ".metaphlan.txt"
		if os.path.exists(expected_output):
			print("Already exists: ", expected_output)
		else:
			mcommand = ["metaphlan2.py", "--input_type", "multifastq", "--bowtie2out", prefix + ".bt2out.txt", "-o", prefix + ".metaphlan.txt"]
			command = " ".join(cat_command) + " | " + " ".join(mcommand)
			print(command)
			os.system(command)
		#process = subprocess.run(cat_command, stdout = subprocess.PIPE, shell = True)

		#subprocess.run(command, stdin = process.stdout)
