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
	samples = collect_moreira_samples(patient_name, output_folder)

	if reference is None or not reference.exists():
		print("reference does not exist. Using {} instead.".format(samples[0].name))
		reference_assembly = assemble_workflow(samples[:1], kmers = "11,21,33,43,55,67,77,87,99,113,127", threads = threads, trim_reads = False)[0]
		reference = reference_assembly.gff

	for sample in samples:
		print("calling variants from ", sample.name)
		print("\treference: ", reference)
		print("\tforward read: ", sample.forward)
		print("\treverse read: ", sample.reverse)
		print("\toutput folder: ", sample.folder)
		variant_call_workflow(reference, sample, threads = threads)
		break


def variant_call_workflow(reference: Path, sample: common.Sample, **kwargs):
	kwargs['parent_folder'] = sample.folder
	threads = kwargs.get('threads', 16)
	common.checkdir(sample.folder)
	trim_reads = False
	read_quality.FastQC.from_sample(sample)
	if trim_reads:
		trim = read_quality.Trimmomatic.from_sample(sample, threads = threads)
		read_quality.FastQC.from_trimmomatic(trim.output)

		variant_callers.Breseq.from_trimmomatic(reference, trim.output, threads = threads)
	else:
		reads = [sample.forward, sample.reverse]
		variant_callers.Breseq.from_list(reference, reads, **kwargs)


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

	fastqc_report = read_quality.FastQC.from_sample(sample)
	trimmed_reads = read_quality.Trimmomatic.from_sample(sample)
	fastqc_trimmed_report = read_quality.FastQC.from_trimmomatic(trimmed_reads.output)

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
	project = Path.home() / "projects" / "moreira_por"
	moreira_output_folder = common.checkdir(project / "variant_calls_untrimmed_reference")
	moreira_reference = None
	moreria_workflow("P148", moreira_output_folder, reference = moreira_reference)


if __name__ == "__main__":
	main()
