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


def workflow(forward_read: Path, reverse_read: Path, parent_folder: Path, genus:str, species:str):
	forward_name = forward_read.stem
	reverse_name = reverse_read.stem
	sample_name = first_common_substring(forward_name, reverse_name)
	prefix = sample_name
	sample_folder = common.checkdir(parent_folder / sample_name)
	prokka_output_folder = sample_folder / "prokka"


	trimmomatic_options = read_quality.TrimmomaticOptions()
	spades_options = read_assembly.SpadesOptions()
	prokka_options = annotation.ProkkaOptions(
		prefix = prefix,
		genus = genus,
		species = species
	)

	trimmomatic_output = read_quality.workflow(forward_read, reverse_read, parent_folder, options = trimmomatic_options, prefix = sample_name)

	spades_output = read_assembly.workflow(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		trimmomatic_output.unpaired_forward,
		sample_folder,
		options = spades_options
	)

def variant_call_workflow(sample_name:Path, forward_read: Path, reverse_read:Path, parent_folder:Path, reference:Path):

	#annotation.prokka(spades_output.contigs, prokka_output_folder, prokka_options)

	if not parent_folder.exists():
		message = f"{parent_folder} does not exist."
		raise ValueError(message)
	else:
		print(f"{parent_folder} exists!")
	sample_folder = common.checkdir(parent_folder / sample_name)

	if not sample_folder.exists():
		message = f"{sample_folder} does not exists"
		raise ValueError(message)
	else:
		print(f"{sample_folder} exists.")

	trimmomatic_options = read_quality.TrimmomaticOptions()
	print("running trimmomatic")
	trimmomatic_output = read_quality.workflow(
		forward_read,
		reverse_read,
		parent_folder,
		options = trimmomatic_options,
		prefix = sample_name
	)
	print("Trimmomatic exists", trimmomatic_output.exists())
	breseq_output = variant_callers.breseq(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		trimmomatic_output.unpaired_forward,
		sample_folder / "breseq_output",
		reference
	)
	return breseq_output


if __name__ == "__main__":
	#import logging



	import pandas
	_sequence_folder = Path.home() / "projects" /"lipuma"/"sequences"/"180707"/"LiPumaStrains"
	project_folder = Path.home() / "projects" / "lipuma"
	parent_folder = project_folder / "pipeline_output"

	if not parent_folder.exists():
		parent_folder.mkdir()
	print("Parent Folder: ", parent_folder)


	reference = project_folder / "AU1054 Reference" / "GCA_000014085.1_ASM1408v1_genomic.gff"
	filename = project_folder / "samples.csv"
	# sampleName
	# forwardRead
	# reverseRead
	table = pandas.read_csv(filename)

	for index, row in table.iterrows():
		#logging.info(f"{index} of {len(table)}")
		print(f"{index} of {len(table)}")
		sample_name = row['sampleName']
		forward = Path(row['forwardRead'])
		reverse = Path(row['reverseRead'])

		r = variant_call_workflow(sample_name, forward, reverse, parent_folder, reference)