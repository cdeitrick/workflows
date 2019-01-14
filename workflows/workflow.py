import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

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
	trimmomatic_options.minimum_length = 70
	trimmomatic_options.leading = 20
	trimmomatic_options.trailing = 20
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


def generate_samplesheet_from_project_folder(folder: Path) -> List[Dict[str, Union[str, Path]]]:
	table = list()
	for sample_folder in folder.iterdir():
		if not folder.is_dir(): continue
		files = list(sample_folder.iterdir())
		sample_name = files[0].name.split('_')[:2]
		sample_name = "_".join(sample_name)
		forward = [i for i in files if 'R1' in i.name][0]
		reverse = [i for i in files if 'R2' in i.name][0]
		row = {
			'sampleName': sample_name,
			'forwardRead':    forward,
			'reverseRead':    reverse
		}
		table.append(row)
	return table


if __name__ == "__main__":
	import pendulum
	import pandas

	# import logging
	sequences = generate_samplesheet_from_project_folder(Path("/home/data/dmux/181218/CooperLabEM/"))
	sequences += generate_samplesheet_from_project_folder(Path("/home/data/dmux/181220/CooperLabEM/"))

	project_folder = Path.home() / "projects" / "eisha"
	# reference = project_folder / "AU1054" / "GCA_000014085.1_ASM1408v1_genomic.gbff"
	reference = Path("/home/cld100/projects/eisha/GCA_000203955.1_ASM20395v1_genomic.fna")
	sample_reference_id = "HI2424"
	parent_folder = project_folder

	if not parent_folder.exists():
		parent_folder.mkdir()
	print("Parent Folder: ", parent_folder)
	table = sequences
	print("Found {} samples".format(len(table)))

	for index, row in enumerate(table):
		# logging.info(f"{index} of {len(table)}")
		sample_name = row['sampleName']
		forward = Path(row['forwardRead'])
		reverse = Path(row['reverseRead'])
		exists = forward.exists() and reverse.exists()
		n = pendulum.now().to_datetime_string()
		print(f"{n}:\t{index} of {len(table)}\t{sample_name}\t{exists}")

		r = variant_call_workflow(sample_name, forward, reverse, parent_folder, reference)
