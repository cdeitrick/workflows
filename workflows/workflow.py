import logging
import sys
from pathlib import Path
from typing import Dict, List, Union

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


def generate_samplesheet_from_project_folder(folder: Path) -> List[Dict[str, Union[str, Path]]]:
	table = list()
	for sample_folder in folder.iterdir():
		try:
			files = list(sample_folder.iterdir())
		except NotADirectoryError:
			continue
		sample_name = files[0].name.split('_')[:2]
		sample_name = "_".join(sample_name)
		forward = [i for i in files if 'R1' in i.name][0]
		reverse = [i for i in files if 'R2' in i.name][0]
		row = {
			'sampleName':  sample_name,
			'forwardRead': forward,
			'reverseRead': reverse
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
	import pendulum

	reference = Path("/home/cld100/projects/lipuma/reference/SC1145/prokka_output/sc1145.gbk")
	project_folder = Path.home() / "projects" / "lipuma"
	parent_folder = project_folder / "au1145_pipeline_output"
	if not parent_folder.exists():
		parent_folder.mkdir()
	sample_list = generate_samplesheet_from_project_folder(project_folder / "sequences")
	whitelist = """SC1128
		SC1129
		SC1145
		SC1209
		SC1210
		SC1211
		SC1339
		AU0465
		SC1371
		SC1392
		SC1400
		AU1051
		AU1057
		AU1055
		AU1056
		SC1407
		SC1419
		SC1420
		SC1421
		SC1435
		AU3741
		AU3739
		AU3740
		AU4359""".split('\n')
	whitelist = [i.strip() for i in whitelist if i]
	total_length = len(sample_list)
	print(f"Found {total_length} samples.")

	sample_list = [i for i in sample_list if i['sampleName'].split('_')[0] in whitelist]

	for index, row in enumerate(sample_list):
		n = pendulum.now()

		sample_name = row['sampleName']
		read1 = row['forwardRead']
		read2 = row['reverseRead']
		print(f"{n}\t{index}\t{sample_name}")
		# if sample_name.split('_')[0] not in whitelist: continue

		variant_call_workflow(sample_name, read1, read2, parent_folder, reference)
