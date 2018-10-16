import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).parent))

try:
	from workflows import read_assembly
	from workflows import annotation
	from workflows import variant_callers
	from workflows import read_quality
	from workflows import common
except ModuleNotFoundError:
	import read_assembly
	import annotation
	import variant_callers
	import read_quality
	import common

"""
	Assemblers -> Annotation -> Breseq

"""


def first_common_substring(seqa: str, seqb: str) -> str:
	for eindex, element in enumerate(zip(seqa, seqb)):
		i, j = element
		if i != j:
			return seqa[:eindex]
	else:
		return seqa


def groupby(collection, by) -> Dict[Any, List[Any]]:
	groups = dict()
	for element in collection:
		key = by(element)
		if key in groups:
			groups[key].append(element)
		else:
			groups[key] = [element]
	return groups


def assemble_workflow(forward_read: Path, reverse_read: Path, parent_folder: Path, genus:str, species:str):
	forward_name = forward_read.stem
	reverse_name = reverse_read.stem
	sample_name = first_common_substring(forward_name, reverse_name)
	prefix = sample_name
	sample_folder = common.checkdir(parent_folder / sample_name)

	trimmomatic_options = read_quality.TrimmomaticOptions()
	spades_options = read_assembly.SpadesOptions()

	trimmomatic_output = read_quality.workflow(forward_read, reverse_read, parent_folder, options = trimmomatic_options, prefix = sample_name)

	spades_output = read_assembly.workflow(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		trimmomatic_output.unpaired_forward,
		sample_folder,
		options = spades_options
	)
	return spades_output

def variant_call_workflow(sample_name:Path, forward_read: Path, reverse_read:Path, parent_folder:Path, reference:Path):

	#annotation.prokka(spades_output.contigs, prokka_output_folder, prokka_options)


	sample_folder = common.checkdir(parent_folder / sample_name)



	trimmomatic_options = read_quality.TrimmomaticOptions()
	print(sample_name)
	print("\t", forward_read)
	print("\t", reverse_read)
	print("running trimmomatic")
	trimmomatic_output = read_quality.workflow(
		forward_read,
		reverse_read,
		sample_folder,
		options = trimmomatic_options,
		prefix = sample_name,
		run_fastqc = False
	)
	print("Running Breseq...")
	breseq_output = variant_callers.breseq(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		trimmomatic_output.unpaired_forward,
		sample_folder / "breseq_output",
		reference
	)
	return breseq_output


if __name__ == "__main__":
	import pandas
	#import logging
	_sequence_folder = Path.home() / "projects" /"lipuma"/"sequences"/"180707"/"LiPumaStrains"
	project_folder = Path.home() / "projects" / "lipuma"
	reference = project_folder / "AU1054" / "GCA_000014085.1_ASM1408v1_genomic.gbff"
	reference_forward_read = project_folder / "sequences" / "071218_20"/ 'AU1581_S20_R1_001.fastq.gz'
	reference_reverse_read = project_folder / "sequences" / "071218_20"/'AU1581_S20_R2_001.fastq.gz'
	filename = project_folder /"samples.tsv"

	parent_folder = project_folder / "cluster2_output"

	if not parent_folder.exists():
		parent_folder.mkdir()
	print("Parent Folder: ", parent_folder)
	#assemble_workflow(reference_forward_read, reference_reverse_read, parent_folder = parent_folder, genus = "Burkholderia", species = "cenocepacia")

	# sampleName
	# forwardRead
	# reverseRead

	table = pandas.read_csv(filename, sep = "\t")
	print("Found {} samples".format(len(table)))
	print(table.to_string())
	for index, row in table.iterrows():
		#logging.info(f"{index} of {len(table)}")

		sample_name = row['sampleName']
		forward = Path(row['forwardRead'])
		reverse = Path(row['reverseRead'])
		exists = forward.exists() and reverse.exists()
		print(f"{index} of {len(table)}\t{sample_name}\t{exists}")

		r = variant_call_workflow(sample_name, forward, reverse, parent_folder, reference)
