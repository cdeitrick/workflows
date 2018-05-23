from pathlib import Path
from typing import List
import sys

sys.path.append(str(Path(__file__).parent))
from dataclasses import dataclass


from . import assemblers
from . import annotation
from . import variant_callers
from . import read_quality


"""
	Assemblers -> Annotation -> Breseq

"""


@dataclass
class Sample:
	name: str
	forward: Path
	reverse: Path
	folder:Path
	def exists(self):
		return self.forward.exists() and self.reverse.exists()


def collect_moreira_samples(output_folder:Path):
	base_name = "P148"
	base_folder = Path.home() / "projects" / "moreira_por"
	isolate_folder = base_folder / "isolates" / "Clinical_isolates_{}".format(base_name)
	samples = list()
	for index in range(1, 100):
		isolate_name = "{}-{}".format(base_name, index)

		forward = isolate_folder / "{}_1.clip1.fastq".format(isolate_name)
		reverse = isolate_folder / "{}_2.clip1.fastq".format(isolate_name)
		sample = Sample(isolate_name, forward, reverse, output_folder / isolate_name)
		if sample.exists():
			samples.append(sample)
		else:
			break
	return samples


def assemble_workflow(samples: List[Sample]):
	# Assemble each sample into reads.

	for sample in samples:
		print("sample ", sample.name)

		fastqc_report = read_quality.FastQC.from_sample(sample)
		trimmed_reads = read_quality.Trimmomatic.from_sample(sample)
		print("trimmomatic output: ", trimmed_reads.output.exists())
		spades_output = assemblers.Spades.from_trimmomatic(trimmed_reads.output, parent_folder = sample.folder)
		print("spades output: ", spades_output.output.exists())
		prokka_output = annotation.Prokka.from_spades(spades_output.output,parent_folder = sample.folder, prefix = sample.name)

def iterate_assemblies(sample:Sample):
	"""
		Generates a number of de novo assemblies with different k-mer sizes.
	Parameters
	----------
	sample

	Returns
	-------

	"""

	fastqc_report = read_quality.FastQC.from_sample(sample)
	trimmed_reads = read_quality.Trimmomatic.from_sample(sample)

	kmer_options = [
		"11,21,33",
		"21,33,43,55,67",
		"21,33,43,55,67,77",
		"21,33,43,55,67,77,87,99",
		"21,33,43,55,67,77,87,99,113",
	]
	for kmer_option in kmer_options:
		output_folder = Path.home() / "projects" / "spades_output_{}".format(kmer_option)
		fwd = trimmed_reads.output.forward
		rev = trimmed_reads.output.reverse
		ufwd= trimmed_reads.output.forward_unpaired
		urev= trimmed_reads.output.reverse_unpaired
		spades = assemblers.Spades(fwd, rev, ufwd, urev, kmer = kmer_option, output_folder = output_folder)

def main():
	debug = False
	if debug:
		output_folder = Path.home() / "projects" / "moreira_por" / "workflow_output"
		moreira_samples = collect_moreira_samples(output_folder)
		if not output_folder.exists():
			output_folder.mkdir()
		assemble_workflow(moreira_samples)
	else:
		sample_name = "P342"
		base_folder = Path.home() / "projects" / "moreira_por"
		isolate_folder = base_folder / "isolates" / "Clinical_isolates_{}".format(sample_name)
		sample = Sample(
			name = sample_name,
			forward = isolate_folder / "{}_1.clip1.fastq".format(sample_name),
			reverse = isolate_folder / "{}_2.clip1.fastq".format(sample_name),
			folder = base_folder / sample_name
		)
		iterate_assemblies(sample)
if __name__ == "__main__":
	main()
