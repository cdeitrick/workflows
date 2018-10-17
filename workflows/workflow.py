import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

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


def assemble_workflow(forward_read: Path, reverse_read: Path, parent_folder: Path, genus: str, species: str):
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


def variant_call_workflow(sample_name: Path, forward_read: Path, reverse_read: Path, parent_folder: Path, reference: Path):
	# annotation.prokka(spades_output.contigs, prokka_output_folder, prokka_options)

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


def get_sample(sample_id: str, folder: Path) -> Tuple[Path, Path]:
	candidates = [i for i in folder.glob("**/*") if i.suffix == '.gz']
	candidates = [i for i in candidates if i.name.startswith(sample_id)]

	forward = [i for i in candidates if 'R1' in i.stem]

	reverse = [i for i in candidates if 'R2' in i.stem]
	print(forward)
	print(reverse)
	return forward[0], reverse[0]


if __name__ == "__main__":
	import pendulum
	import pandas

	# import logging
	_sequence_folder = Path.home() / "projects" / "lipuma" / "sequences" / "180707" / "LiPumaStrains"
	project_folder = Path.home() / "projects" / "lipuma"
	reference = project_folder / "AU1054" / "GCA_000014085.1_ASM1408v1_genomic.gbff"
	sample_reference_id = "AU1836"
	sample_table_filename = project_folder / "samples.tsv"
	reference_forward_read, reference_reverse_read = get_sample(sample_reference_id, project_folder / "sequences")
	parent_folder = project_folder / "AU1836_output"

	if not parent_folder.exists():
		parent_folder.mkdir()
	print("Parent Folder: ", parent_folder)
	# assemble_workflow(reference_forward_read, reference_reverse_read, parent_folder = parent_folder, genus = "Burkholderia", species = "cenocepacia")

	# sampleName
	# forwardRead
	# reverseRead

	table = pandas.read_csv(sample_table_filename, sep = "\t")
	print("Found {} samples".format(len(table)))
	#print(table.to_string())
	assemble = True
	if assemble:
		assemble_workflow(reference_forward_read, reference_reverse_read,parent_folder, "burkholderia", "cenocepacia")
	else:
		for index, row in table.iterrows():
			# logging.info(f"{index} of {len(table)}")

			sample_name = row['sampleName']
			forward = Path(row['forwardRead'])
			reverse = Path(row['reverseRead'])
			exists = forward.exists() and reverse.exists()
			n = pendulum.now().to_datetime_string()
			print(f"{n}:\t{index} of {len(table)}\t{sample_name}\t{exists}")

			r = variant_call_workflow(sample_name, forward, reverse, parent_folder, reference)
