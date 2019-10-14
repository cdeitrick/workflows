"""
The entry point for scripts using the piplelines.
"""
from pathlib import Path
from typing import Dict, List

from loguru import logger

from pipelines import sampleio
from pipelines.processes import read_trimming
from pipelines.processes.variant_calling import sample_variant_calling
from pipelines import programio


def read_sample_map(filename: Path) -> Dict[str, str]:
	contents = filename.read_text()
	lines = contents.split('\n')
	lines = [i.strip() for i in lines]
	kvs = [i.split('\t') for i in lines]
	data = dict()
	for k, v in kvs:
		data[k] = v
	return data


def test_found_all_samples(samples: List[sampleio.SampleReads], expected: int):
	try:
		assert len(samples) == expected
	except AssertionError:
		from pprint import pprint
		message = f"Expected {expected} samples, but found {len(samples)}"
		raise ValueError(message)


def transposon_variant_calling():
	project_folder = Path.home() / "projects" / "yiwei"
	sample_folder = project_folder / "WozniakLab"

	samples = [sampleio.SampleReads.from_folder(subfolder) for subfolder in sample_folder.iterdir()]

	reference = project_folder / "GCF_000006765.1_ASM676v1" / "GCF_000006765.1_ASM676v1_genomic.gbff"

	sample_variant_calling(reference, samples, project_folder / "breseq")


def main_mworkshop():
	logger.info("Running variant pipeline...")
	maxwell_folder = Path("/home/cld100/projects/migs/MaxwellLab")
	sample_folder = maxwell_folder / "samples"

	# reference = sampleio.SampleReads.from_folder(sample_folder / "100419_42", sample_id = "PA01_EV")

	# read_trimming.trim([reference],parent_folder = maxwell_folder, stringent = True)
	# reference_assembly = read_assembly.read_assembly([reference], maxwell_folder, stringent = True)[0]
	# reference_assembly = Path(maxwell_folder / "PA01_EV" / "prokka" / "PA01_EV.gff")
	# sample_reads = list()
	# for folder in sample_folder.iterdir():
	#	sample_reads.append(sampleio.SampleReads.from_folder(folder))
	# trimmomatic_files = read_trimming.trim(sample_reads, maxwell_folder)
	# trimmomatic_files = [i.as_sample() for i in trimmomatic_files]
	folder = Path("/home/cld100/projects/workshop")
	reference_assembly = folder / "AU1054 GENBANK" / "AU1054 GENBANK/GCA_000014085.1_ASM1408v1_genomic.gbff"
	sample_folder = folder / "reads_trimmed"
	trimmomatic_files = list()
	for i in sample_folder.iterdir():
		trimmomatic_files.append(programio.TrimmomaticOutput.from_folder(i, i.name))
	trimmomatic_files = [i.as_sample() for i in trimmomatic_files]

	sample_variant_calling(reference_assembly, trimmomatic_files, maxwell_folder)