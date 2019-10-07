"""
The entry point for scripts using the piplelines.
"""
from pathlib import Path
from typing import Dict, List, Union

from loguru import logger

from pipelines import sampleio
from pipelines.processes import read_assembly, read_trimming
from pipelines.processes.variant_calling import sample_variant_calling


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


def checkdir(path: Path) -> Path:
	path = Path(path)
	if not path.exists():
		path.mkdir()
	return path


def mainassembly():
	logger.info("Running Assembly pipeline...")
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	update_folder = checkdir(lipuma_folder / "2019-07-24-update")
	pipeline_folder = checkdir(update_folder / "assembly_trimmed_major")
	source_folder = lipuma_folder / "genomes" / "reads" / "trimmedMajor"

	folders = list(source_folder.iterdir())
	samples = [sampleio.SampleReads.from_trimmomatic(i, i.name) for i in folders]

	read_assembly.read_assembly(samples, pipeline_folder)


def breseq_main():
	lipuma_folder = Path("/home/cld100/projects/lipuma")

	parent_folder = lipuma_folder / "pipelines" / "pairwise_pipeline_shovill"
	reference_folder = lipuma_folder / "genomes" / "assembly" / "assembly_shovill_annotated"
	sample_folder = lipuma_folder / "genomes" / "reads" / "trimmed"
	isolate_map_filename = lipuma_folder / "isolate_sample_map.old.txt"

	# Import isolate map
	lines = isolate_map_filename.read_text().split('\n')
	pairs = [i.strip().split('\t') for i in lines if i]
	pairs = {i: j for i, j in pairs}

	au1064 = reference_folder / "AU1064" / "AU1064.gff"
	sc1360 = reference_folder / "SC1360" / "SC1360.gff"

	sc1128 = reference_folder / "SC1128" / "SC1128.gff"
	sc1145 = reference_folder / "SC1145" / "SC1145.gff"

	au1836 = reference_folder / "AU1836" / "AU1836.gff"
	au3415 = reference_folder / "AU3415" / "AU3415.gff"

	au0075 = reference_folder / "AU0075" / "AU0075.gff"
	au15033 = reference_folder / "AU15033" / "AU15033.gff"

	logger.info(f"Collecting all PHDC samples...")
	all_sample_folders = list(sample_folder.iterdir())
	patient_samples = {'A': list(), 'B': list(), 'E': list(), 'F': list()}
	for sample_folder in all_sample_folders:
		sample_id = sample_folder.name
		remap = pairs.get(sample_id)
		if remap:
			patient_id = remap[0]
			patient_samples[patient_id].append(sample_folder)

	for k, v in patient_samples:
		logger.info(f"found {len(v)} samples for patient pair {k}")

	sample_variant_calling(au1064, patient_samples['A'], checkdir(parent_folder / "AU1064"))
	sample_variant_calling(sc1360, patient_samples['A'], checkdir(parent_folder / "SC1360"))
	sample_variant_calling(sc1128, patient_samples['B'], checkdir(parent_folder / "SC1128"))
	sample_variant_calling(sc1145, patient_samples['B'], checkdir(parent_folder / "SC1145"))
	sample_variant_calling(au1836, patient_samples['E'], checkdir(parent_folder / "AU1836"))
	sample_variant_calling(au3415, patient_samples['E'], checkdir(parent_folder / "AU3415"))
	sample_variant_calling(au0075, patient_samples['F'], checkdir(parent_folder / "AU0075"))
	sample_variant_calling(au15033, patient_samples['F'], checkdir(parent_folder / "AU15033"))


def main_variant_calling():
	logger.info("Running variant pipeline...")
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	update_folder = checkdir(lipuma_folder / "2019-07-24-update")
	reference_folder = update_folder / "reference_samples"
	pipeline_folder = checkdir(update_folder / "pairwise_pipeline")

	references = [
		reference_folder / "AU1064" / "annotations" / "AU1064.gff",
		reference_folder / "SC1360" / "annotations" / "SC1360.gff",
		reference_folder / "SC1128" / "annotations" / "SC1128.gff",
		reference_folder / "SC1145" / "annotations" / "SC1145.gff",
		reference_folder / "AU1836" / "annotations" / "AU1836.gff",
		reference_folder / "AU3415" / "annotations" / "AU3415.gff",
		reference_folder / "AU0075" / "annotations" / "AU0075.gff",
		reference_folder / "AU15033" / "annotations" / "AU15033.gff",
	]

	sequence_folder = lipuma_folder / "genomes" / "reads" / "trimmedMajor"

	samples = list()
	for sample_read_folder in sequence_folder.iterdir():
		try:
			sample = sampleio.SampleReads.from_trimmomatic(sample_read_folder, sample_read_folder.name)
		except:
			logger.warning(f"Could not collect the reads from folder {sample_read_folder}")
			continue
		samples.append(sample)

	sample_name_map_filename = lipuma_folder / "isolate_sample_map.old.txt"
	sample_name_map = read_sample_map(sample_name_map_filename)
	print(sample_name_map)
	sibling_pair_a_ids = [k for k, v in sample_name_map.items() if (v.startswith('A0') or v.startswith('A1'))]
	sibling_pair_b_ids = [k for k, v in sample_name_map.items() if (v.startswith('B0') or v.startswith('B1'))]
	sibling_pair_e_ids = [k for k, v in sample_name_map.items() if (v.startswith('E0') or v.startswith('E1'))]
	sibling_pair_f_ids = [k for k, v in sample_name_map.items() if (v.startswith('F0') or v.startswith('F1'))]

	sibling_pair_a_samples = [i for i in samples if i.name in sibling_pair_a_ids]
	sibling_pair_b_samples = [i for i in samples if i.name in sibling_pair_b_ids]
	sibling_pair_e_samples = [i for i in samples if i.name in sibling_pair_e_ids]
	sibling_pair_f_samples = [i for i in samples if i.name in sibling_pair_f_ids]

	logger.info(f"sibling pair a: {len(sibling_pair_a_samples)}")
	logger.info(f"sibling pair b: {len(sibling_pair_b_samples)}")
	logger.info(f"sibling pair e: {len(sibling_pair_e_samples)}")
	logger.info(f"sibling pair f: {len(sibling_pair_f_samples)}")

	test_found_all_samples(sibling_pair_a_samples, 25)
	test_found_all_samples(sibling_pair_b_samples, 25)
	test_found_all_samples(sibling_pair_e_samples, 27)
	test_found_all_samples(sibling_pair_f_samples, 18)

	samples = {
		'A': sibling_pair_a_samples,
		'B': sibling_pair_b_samples,
		'E': sibling_pair_e_samples,
		'F': sibling_pair_f_samples
	}

	for reference, pair_id in zip(references, ['A', 'A', 'B', 'B', 'E', 'E', 'F', 'F']):
		parent_folder = checkdir(pipeline_folder / reference.stem)
		current_samples = samples[pair_id]
		sample_variant_calling(reference, current_samples, parent_folder)


def transposon_variant_calling():
	project_folder = Path.home() / "projects" / "yiwei"
	sample_folder = project_folder / "WozniakLab"

	samples = [sampleio.SampleReads.from_folder(subfolder) for subfolder in sample_folder.iterdir()]

	reference = project_folder / "GCF_000006765.1_ASM676v1" / "GCF_000006765.1_ASM676v1_genomic.gbff"

	sample_variant_calling(reference, samples, project_folder / "breseq")


def main_migs_maxwelllab_variant_calling():
	logger.info("Running variant pipeline...")
	maxwell_folder = Path("/home/cld100/projects/migs/MaxwellLab")
	sample_folder = maxwell_folder / "samples"
	reference = sampleio.SampleReads.from_folder(sample_folder / "100419_42", sample_id = "PA01_EV")

	reference_assembly = read_assembly.read_assembly([reference], maxwell_folder, stringent = True)[0]

	#sample_reads = list()
	#for folder in sample_folder.iterdir():
	#	if folder.name.endswith('42'): continue
	#	sample_reads.append(sampleio.SampleReads.from_folder(folder))
	#trimmomatic_files = read_trimming.trim(sample_reads, maxwell_folder)
	#trimmomatic_files = [i.as_sample() for i in trimmomatic_files]
	#sample_variant_calling(reference_assembly.contigs, trimmomatic_files, maxwell_folder)


def main_variant_calling_generic(sample_folder: Path, reference: Union[str, Path], output_folder: Path):
	pass
