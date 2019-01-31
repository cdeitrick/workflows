import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
import logging
logger = logging.getLogger(__name__)
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


def assemble_workflow(forward_read: Path, reverse_read: Path, parent_folder: Path):
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
	reference = Path("/home/cld100/projects/lipuma/reference/SC1145/GCA_000014085.1_ASM1408v1_genomic.fasta")
	spades_options.reference = reference
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

def groupby(key, sequence):
	groups = dict()
	for item in sequence:
		item_key = key(item)
		if item_key in groups:
			groups[item_key].append(item)
		else:
			groups[item_key] = [item]
	return groups

if __name__ == "__main__":
	"""
	import pendulum

	project_folder = Path.home() / "projects" / "riptide"
	sequences = groupby(lambda s: "-".join(s.name.split('-')[:2]), (project_folder / "fastqs").iterdir())
	reference = Path("/home/data/refs/hi2424_180206.gbk")

	parent_folder = project_folder

	if not parent_folder.exists():
		parent_folder.mkdir()
	print("Found {} samples".format(len(sequences)))
	index = 0
	for sample_name, filenames in sequences.items():
		index += 1
		forward = [i for i in filenames if 'R1' in i.name][0]
		reverse = [i for i in filenames if 'R2' in i.name][0]
		n = pendulum.now().to_datetime_string()

		print(f"{n}:\t{index} of {len(sequences)}\t{sample_name}")
		r = variant_call_workflow(sample_name, forward, reverse, parent_folder, reference)
	"""
	folder = Path("/home/cld100/projects/lipuma/reference/SC1145")
	read1 = folder / "SC1145_S52_R1_001.fastq.gz"
	read2 = folder / "SC1145_S52_R2_001.fastq.gz"

	assemble_workflow(read1, read2, folder)
