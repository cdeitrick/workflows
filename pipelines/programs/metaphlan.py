from typing import List, Any
from pipelines import sampleio
from pathlib import Path

def run_metaphlan(samples: List[sampleio.SampleReads], output_folder: Path, bash: Path = None):
	"""
		Runs metaphlan over a series of samples.
	Parameters
	----------
	samples
	output_folder: Where to save the output
	bash:Path Will write the command to this file
	"""

	commands: List[List[Any]] = list()
	for sample in samples:
		command = ["metaphlan2.py", "--input_type", "fastq", "-o", output_folder, sample.forward]

		commands.append(command)

	with bash.open('w') as file1:
		for command in commands:
			string_command = " ".join([str(i) for i in command])
			file1.write(string_command + '\n\n')