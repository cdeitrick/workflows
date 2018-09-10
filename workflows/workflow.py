import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

sys.path.append(str(Path(__file__).parent))
import argparse
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
def groupby(collection, by)->Dict[Any,List[Any]]:
	groups = dict()
	for element in collection:
		key = by(element)
		if key in groups:
			groups[key].append(element)
		else:
			groups[key] = [element]
	return groups

def collect_samples(base_name: str, output_folder: Path):
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


def project_workflow(patient_name: str, output_folder: Path, reference: Optional[Path] = None, **kwargs):
	threads = kwargs.get('threads', 16)
	if 'run_all' in kwargs:
		run_all = kwargs['run_all']
		del kwargs['run_all']
	else:
		run_all = False
	common.checkdir(output_folder)
	print("Reference: ", reference.exists()if reference is not None else False, reference)
	samples = collect_samples(patient_name, output_folder)

	if reference is None or not reference.exists():
		print("reference does not exist. Using {} instead.".format(samples[0].name))
		reference_assembly = assemble_workflow(samples[:1], kmers = "11,21,33,43,55,67,77,87,99,113,127", threads = threads, trim_reads = False)[0]
		reference = reference_assembly.gff
		print("Reference File: ", reference.exists(), reference)

	_breakpoint = Path.home() / "_breakpoint_file.txt"
	for sample in samples:
		if not _breakpoint.exists() or not run_all: break
		print("calling variants from {} (started at {})".format(sample.name, datetime.datetime.now().isoformat()))
		print("\treference: ", reference)
		print("\tforward read: ", sample.forward)
		print("\treverse read: ", sample.reverse)
		print("\toutput folder: ", sample.folder)
		variant_call_workflow(reference, sample, threads = threads)



def variant_call_workflow(reference: Path, sample: common.Sample, **kwargs):
	kwargs['parent_folder'] = sample.folder
	kwargs['threads'] = kwargs.get('threads', 16)
	common.checkdir(sample.folder)
	trim_reads = True
	read_quality.FastQC.from_sample(sample)
	if trim_reads:
		trim = read_quality.Trimmomatic.from_sample(sample, **kwargs)
		read_quality.FastQC.from_trimmomatic(trim.output)

		variant_callers.Breseq.from_trimmomatic(reference, trim.output, **kwargs)
	else:
		variant_callers.Breseq.from_sample(reference, sample, **kwargs)

def dmux_workflow(reference:Path, dmux_folder:Path, output_folder:Path):

	dmux_samples = list(i for i in dmux_folder.glob("**/*") if (i.suffix == '.gz'))

	dmux_samples = filter(lambda s: s.stem.split('_')[3] not in {'I1', 'I2'}, dmux_samples)

	groups = groupby(dmux_samples, lambda s: '_'.join(s.stem.split('_')[:3]))

	print(len(groups))
	index = 0
	for stem, samples in sorted(groups.items()):
		index += 1
		print("Processing {} ({} of {})".format(stem, index, len(groups)))
		forward_read = [i for i in samples if i.stem.split('_')[3] == 'R1'][0]
		reverse_read = [i for i in samples if i.stem.split('_')[3] == 'R2'][0]
		sample = common.Sample(
			name = stem,
			forward = forward_read,
			reverse = reverse_read,
			folder = output_folder
		)

		trimmomatic_output = read_quality.Trimmomatic.from_sample(sample)
		variant_callers.Breseq.from_trimmomatic(reference, trimmomatic_output.output)

		if index > 3:
			break



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
	reference = Path("/home/vclocal/ref/Staphylococcus_aureus_Newman.gbk")
	dmux_folder = Path("/home/dmux/180906/SkaarLab/")
	output_folder = Path("/home/dmux/workflow/")

	print(reference.exists(), reference)


	if not output_folder.exists(): output_folder.mkdir()

	dmux_workflow(reference, dmux_folder, output_folder)
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
