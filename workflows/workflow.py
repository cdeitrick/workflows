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
	for index, element in enumerate(zip(seqa, seqb)):
		i, j = element
		if i != j:
			return seqa[:index]
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
	parent_folder = parent_folder / sample_name
	prokka_output_folder = parent_folder / "prokka"


	trimmomatic_options = read_quality.TrimmomaticOptions()
	spades_options = read_assembly.SpadesOptions()
	prokka_options = annotation.ProkkaOptions(
		prefix = prefix,
		genus = genus,
		species = species
	)

	trimmomatic_output = read_quality.workflow(forward_read, reverse_read, parent_folder, options = trimmomatic_options)

	spades_output = read_assembly.workflow(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		trimmomatic_output.unpaired_forward,
		parent_folder,
		options = spades_options
	)

	annotation.prokka(spades_output.contigs, prokka_output_folder, prokka_options)


if __name__ == "__main__":
	_sequence_folder = Path.home() / "projects" /"lipuma"/"sequences"/"180707"/"LiPumaStrains"/"070818_01"

	_forward_read = _sequence_folder / "AU23516_S1_R1_001.fastq.gz"
	_reverse_read = _sequence_folder / "AU23516_S1_R2_001.fastq.gz"
	parent_folder = Path.home() / "sample_output"
	common.checkdir(parent_folder)
	genus = "Burkholderia"
	species = "cenocepacia"

	workflow(_forward_read, _reverse_read, parent_folder, genus, species)
