import sys
from pathlib import Path
from typing import List, Optional

sys.path.append(str(Path(__file__).parent))

try:
	from . import assemblers
	from . import annotation
	from . import variant_callers
	from . import read_quality
	from . import common
except:
	import assemblers
	import annotation
	import variant_callers
	import read_quality
	import common

"""
	Assemblers -> Annotation -> Breseq

"""


def collect_moreira_samples(base_name: str, output_folder: Path):
	base_folder = Path.home() / "projects" / "moreira_por"
	isolate_folder = base_folder / "isolates" / "Clinical_isolates_{}".format(base_name)
	samples = list()
	for index in range(1, 100):
		isolate_name = "{}-{}".format(base_name, index)

		forward = isolate_folder / "{}_1.clip1.fastq".format(isolate_name)
		reverse = isolate_folder / "{}_2.clip1.fastq".format(isolate_name)
		sample = common.Sample(isolate_name, forward, reverse, output_folder / isolate_name)
		if sample.exists():
			samples.append(sample)
		else:
			break
	return samples


def moreria_workflow(patient_name: str, output_folder: Path, reference: Optional[Path] = None, **kwargs):
	threads = kwargs.get('threads', 16)
	common.checkdir(output_folder)
	print("Output Folder: ", output_folder)
	print("Reference: ", reference.exists()if reference is not None else False, reference)
	samples = collect_moreira_samples(patient_name, output_folder)
	print("Found Samples: ")
	for i in samples:
		print("\t", i)
	if reference is None or not reference.exists():
		print("reference does not exist. Using {} instead.".format(samples[0].name))
		reference_assembly = assemble_workflow(samples[:1], kmers = "11,21,33,43,55,67,77,87,99,113,127", threads = threads, trim_reads = False)[0]
		reference = reference_assembly.gff
	_breakpoint = Path.home() / "_breakpoint_file.txt"
	for sample in samples:
		if not _breakpoint.exists(): break
		print("calling variants from ", sample.name)
		print("\treference: ", reference)
		print("\tforward read: ", sample.forward)
		print("\treverse read: ", sample.reverse)
		print("\toutput folder: ", sample.folder)
		variant_call_workflow(reference, sample, threads = threads)



def variant_call_workflow(reference: Path, sample: common.Sample, **kwargs):
	kwargs['parent_folder'] = sample.folder
	threads = kwargs.get('threads', 16)
	common.checkdir(sample.folder)

	read_quality.FastQC.from_sample(sample)

	trim = read_quality.Trimmomatic.from_sample(sample, threads = threads)
	read_quality.FastQC.from_trimmomatic(trim.output)

	variant_callers.Breseq.from_trimmomatic(reference, trim.output, threads = threads)



def assemble_workflow(samples: List[common.Sample], **kwargs) -> List[annotation.ProkkaOutput]:
	# Assemble each sample into reads.

	kwargs['threads'] = kwargs.get('threads', 16)

	output_files = list()
	for sample in samples:
		print("Assemble Workflow Sample: ", sample.name)
		print("Output Folder: ", sample.folder)
		common.checkdir(sample.folder)

		read_quality.FastQC.from_sample(sample)

		trimmed_reads = read_quality.Trimmomatic.from_sample(sample, **kwargs)
		read_quality.FastQC.from_trimmomatic(trimmed_reads.output)

		spades_output = assemblers.SpadesWorkflow.from_trimmomatic(trimmed_reads.output, parent_folder = sample.folder,
															   **kwargs)

		prokka_output = annotation.Prokka.from_spades(spades_output.output, parent_folder = sample.folder,
													  prefix = sample.name, **kwargs)
		output_files.append(prokka_output.output)
	return output_files


def iterate_assemblies(sample: common.Sample):
	"""
		Generates a number of de novo assemblies with different k-mer sizes.
	Parameters
	----------
	sample

	Returns
	-------

	"""

	read_quality.FastQC.from_sample(sample)
	trimmed_reads = read_quality.Trimmomatic.from_sample(sample)
	read_quality.FastQC.from_trimmomatic(trimmed_reads.output)

	kmer_options = [
		"11,21,33,43",
		"33,43,55,67",
		"43,55,67,77",
		"55,67,77,87,99",
		"67,77,87,99,113",
		"11,21,33,43,55,67,77,87,99,113,127"
	]
	for kmer_option in kmer_options:
		output_folder = Path.home() / "projects" / "spades_output_{}".format(kmer_option)
		fwd = trimmed_reads.output.forward
		rev = trimmed_reads.output.reverse
		ufwd = trimmed_reads.output.forward_unpaired
		urev = trimmed_reads.output.reverse_unpaired
		spades = assemblers.SpadesWorkflow(fwd, rev, ufwd, urev, kmers = kmer_option, output_folder = output_folder)


def main():
	patient_name = "P342"
	project = Path.home() / "projects" / "moreira_por"
	moreira_output_folder = common.checkdir(project / "variant_calls_{}".format(patient_name))
	moreira_reference = project / "variant_calls" / "{}-1".format(patient_name) / "prokka_output" / "{}-1.gff".format(patient_name)
	#moreira_reference = project / "references" / "GCA_000010545.1_ASM1054v1_cds_from_genomic.fna"
	moreira_reference = None
	moreria_workflow(patient_name, moreira_output_folder, reference = moreira_reference)

def get_environment_details():
	import subprocess
	environment_details_path = Path(__file__).with_name('last_run_environment.txt')
	command = ['module', 'list']
	#process = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding = 'utf-8')
	#environment_details_path.write_text(process.stdout)
	import os
	command = "module list | > {}".format(environment_details_path.absolute())
	print(command)
	import sys
	print(sys.path)
	os.system(command)


if __name__ == "__main__":
	main()
