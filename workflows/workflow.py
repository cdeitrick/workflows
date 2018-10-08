import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).parent))

try:
	from . import read_assembly
	from . import annotation
	from . import variant_callers
	from . import read_quality
	from . import common
except:
	import read_assembly
	import annotation
	import variant_callers
	import read_quality
	import common

"""
	Assemblers -> Annotation -> Breseq

"""


def first_common_substring(seqa: str, seqb: str) -> str:
	for index, element in zip(seqa, seqb):
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


def workflow(forward_read: Path, reverse_read: Path, output_folder: Path):
	forward_name = forward_read.stem
	reverse_name = reverse_read.stem
	sample_name = first_common_substring(forward_name, reverse_name)
	sample_output_folder = output_folder / sample_name

	fastqc_output_folder = sample_output_folder / "fastqc_raw"
	fastqc_trimmed_output_folder = sample_output_folder / "fastqc_trimmed"
	trimmomatic_output_folder = sample_output_folder / "trimmomatic"
	spades_output_folder = sample_output_folder / "spades"
	bandage_output_folder = sample_output_folder / "bandage"
	prokka_output_folder = sample_output_folder / "prokka"
	breseq_output_folder = sample_output_folder / "breseq"

	trimmomatic_options = read_quality.TrimmomaticOptions()
	spades_options = read_assembly.SpadesOptions()
	prokka_options = annotation.ProkkaOptions()

	trimmomatic_output = read_quality.workflow(forward_read, reverse_read, trimmomatic_output_folder, options = trimmomatic_options)

	spades_output = read_assembly.workflow(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		trimmomatic_output.unpaired_forward,
		spades_output_folder,
		options = spades_options
	)

	prokka_output = annotation.prokka(spades_output.contigs, prokka_output_folder, prokka_options)


if __name__ == "__main__":
	workflow()
