from pathlib import Path
from typing import List, Dict
import sys

sys.path.append(str(Path(__file__).parent))
from dataclasses import dataclass
try:
	from . import assemblers
	from . import annotation
	from . import variant_callers

except:
	import assemblers
	import annotation
	import variant_callers

"""
	Assemblers -> Annotation -> Breseq

"""

@dataclass
class Sample:
	name: str
	forward: Path
	reverse: Path

	def exists(self):
		return self.forward.exists() and self.reverse.exists()

def collect_moreira_samples():
	base_name = "P148"
	base_folder = Path.home() / "projects" / "moreira_por"
	isolate_folder = base_folder / "IST-Leonilde" / "Seq.Vaughn" / "Clinical_isolates_{}".format(base_name)
	samples = list()
	for index in range(1, 100):
		isolate_name = "{}-{}".format(base_name, index)

		forward = isolate_folder / "{}_1.clip1.fastq".format(isolate_name)
		reverse = isolate_folder / "{}_2.clip1.fastq".format(isolate_name)
		sample = Sample(isolate_name, forward, reverse)
		print(sample.exists(), sample)
		if sample.exists():
			samples.append(sample)
		else:
			break
	return samples


def assemble_workflow(output_folder:Path, samples:List[Sample]):

	# Assemble each sample into reads.

	for sample in samples:
		trimmed_reads = assemblers.Trimmomatic.from_sample(output_folder, sample)
		spades_output = assemblers.Spades.from_trimmomatic(trimmed_reads.output, parent_folder = output_folder)
		prokka_output = annotation.Prokka.from_spades(spades_output.output)


if __name__ == "__main__":
	moreira_samples = collect_moreira_samples()
	print("collected {} samples".format(len(moreira_samples)))
	output_folder = Path.home() / "projects" / "moreira_por" / "workflow_output"
	if not output_folder.exists():
		output_folder.mkdir()
	assemble_workflow(output_folder, moreira_samples)