import logging
import sys
from pathlib import Path
from typing import Dict, List, Union, Optional
import sys

from loguru import logger
sys.path.append(str(Path(__file__).parent))

try:
	from workflows import read_assembly
	from workflows import annotation
	from workflows import variant_callers
	from workflows import read_quality
	from workflows import common
	from workflows import sampleio
except ModuleNotFoundError:
	import read_assembly
	import annotation
	import variant_callers
	import read_quality
	import common
	import sampleio

"""
	Assemblers -> Annotation -> Breseq

"""

REFERENCE_AU1054 = Path("/home/cld100/projects/lipuma/reference/AU1054/GCA_000014085.1_ASM1408v1_genomic.fna")


def first_common_substring(seqa: str, seqb: str) -> str:
	for eindex, element in enumerate(zip(seqa, seqb)):
		i, j = element
		if i != j:
			return seqa[:eindex]
	else:
		return seqa


def assemble_workflow(forward_read: Path, reverse_read: Path, parent_folder: Path, trusted_contigs: Optional[Path] = None):
	"""
		Assembles the provided reads.
		[original reads] -> Trimmomatic -> Spades
	Parameters
	----------
	forward_read: Path
		The untrimmed forward read
	reverse_read: Path
		The untrimmed reverse read
	parent_folder: Path
	trusted_contigs: Optional[Path]
	"""
	parameters = {'forward_read': forward_read, 'reverse_read': reverse_read, 'parent_folder': parent_folder}
	logger.info("running the assembly workflow")
	logger.debug(parameters)

	forward_name = forward_read.stem
	reverse_name = reverse_read.stem

	sample_name = first_common_substring(forward_name, reverse_name)
	logger.debug(f"Sample Name: {sample_name}")
	sample_folder = common.checkdir(parent_folder / sample_name)
	logger.debug(f"Sample folder: {sample_folder}")

	trimmomatic_options = read_quality.TrimmomaticOptions(
		minimum_length = 70,
		leading = 20,
		trailing = 20
	)

	spades_options = read_assembly.SpadesOptions(reference = trusted_contigs)

	trimmomatic_output = read_quality.workflow(forward_read, reverse_read, parent_folder, options = trimmomatic_options, prefix = sample_name)
	"""
	spades_output = read_assembly.spades(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		sample_folder / "spades",
		options = spades_options
	)
	"""
	shovill_output = read_assembly.shovill(
		trimmomatic_output.forward,
		trimmomatic_output.reverse,
		sample_folder / "shovill",
		options = spades_options
	)



def variant_call_workflow(sample_name: str, forward_read: Path, reverse_read: Path, pipeline_output_folder: Path, reference: Path):
	# annotation.prokka(spades_output.contigs, prokka_output_folder, prokka_options)

	sample_folder = common.checkdir(pipeline_output_folder / sample_name)

	trimmomatic_options = read_quality.TrimmomaticOptions()
	logger.info(sample_name)
	logger.info(f"\tforward read: {forward_read}")
	logger.info(f"\treverse_read: {reverse_read}")
	logger.info(f"\toutput folder: {sample_folder}")
	logger.info("running trimmomatic")
	trimmomatic_output = read_quality.workflow(
		forward_read,
		reverse_read,
		sample_folder,
		options = trimmomatic_options,
		prefix = sample_name,
		run_fastqc = False
	)
	logger.info("Running Breseq...")
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


def load_sample_map(filename: Path) -> Dict[str, str]:
	contents = filename.read_text().split('\n')
	sample_map = dict()
	for line in contents:
		line = line.strip()
		try:
			i, j = line.split('\t')
			sample_map[i] = j
		except:
			pass
	return sample_map

_variants = False
if __name__ == "__main__" and _variants:
	folder = Path("/home/cld100/projects/lipuma/samples")

	reference_folder = folder.parent / "reference_assemblies"
	a1_sample = Path(reference_folder / "SC1360" / "prokka_output" / "SC1360.gff")
	a2_sample = Path(reference_folder / "AU1064" / "prokka_output" / "AU1064.gff")
	b1_sample = Path(reference_folder / "SC1128" / "prokka_output" / "SC1128.gff")
	b2_sample = Path(reference_folder / "SC1145" / "prokka_output" / "SC1145.gff")
	e1_sample = Path(reference_folder / "AU3415" / "prokka_output" / "AU3415.gff")
	e2_sample = Path(reference_folder / "AU1836" / "prokka_output" / "AU1836.gff")
	f1_sample = Path(reference_folder / "AU0074" / "prokka_output" / "AU0074.gff")
	f2_sample = Path(reference_folder / "AU15033" / "prokka_output" / "AU15033.gff")
	r1_sample = Path(reference_folder / "AU1054" / "GCA_000014085.1_ASM1408v1_genomic.gbk")
	references = [a1_sample, a2_sample, b1_sample, b2_sample, e1_sample, e2_sample, f1_sample, f2_sample, r1_sample]
	for ref in references:
		logger.info(f"Reference Exists: {ref.exists()}\t{ref}")
	patients = "A|A|B|B|E|E|F|F|A".split('|')

	references = reversed(references)
	patients = reversed(patients)

	samples = list()
	for sample_folder in folder.iterdir():
		try:
			sample = sampleio.Sample.from_folder(sample_folder)
			samples.append(sample)
		except:
			pass
	logger.info(f"Found {len(samples)} samples.")
	sample_map_filename = Path("/home/cld100/projects/lipuma/isolate_sample_map.tsv")
	sample_map = load_sample_map(sample_map_filename)
	output_folder = Path("/home/cld100/projects/lipuma/pairwise_pipeline")

	for reference_label, reference_filename in zip(patients, references):
		logger.info(f"Running pipeline for {reference_filename}")
		reference_pipeline_output_folder = output_folder / reference_filename.stem
		if not reference_pipeline_output_folder.exists():
			reference_pipeline_output_folder.mkdir()

		pipeline_samples = [i for i in samples if sample_map.get(i.name, "").startswith(reference_label)]
		logger.info(f"Found {len(pipeline_samples)} samples for this reference.")
		for index, sample in enumerate(pipeline_samples):
			logger.info(f"Running pipeline for sample {index} of {len(pipeline_samples)}.")
			if reference_pipeline_output_folder.joinpath(sample.name).exists(): continue
			variant_call_workflow(sample.name, sample.forward, sample.reverse, reference_pipeline_output_folder, reference_filename)
else:
	output_folder = Path("/home/cld100/projects/lipuma/shovill_assemblies")
	if not output_folder.exists():
		output_folder.mkdir()
	sample_folder = Path("/home/cld100/projects/lipuma/samples/AU1064")

	assemble_workflow(
		sample_folder / "AU1064_S14_R1_001.fastq",
		sample_folder / "AU1064_S14_R2_001.fastq",
		parent_folder = output_folder
	)