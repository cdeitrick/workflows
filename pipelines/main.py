"""
The entry point for scripts using the piplelines.
"""
from pathlib import Path
from typing import Dict

from loguru import logger

from pipelines import sampleio
from pipelines.processes import read_assembly
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


def checkdir(path: Path) -> Path:
	path = Path(path)
	if not path.exists():
		path.mkdir()
	return path


def mainassembly():
	logger.info("Running Assembly pipeline...")
	source_folder = Path("/home/cld100/projects/lipuma/genomes/reads/trimmed/")
	parent_folder = source_folder.with_name('trimmed_stringent')

	folders = list(source_folder.iterdir())
	samples = [sampleio.SampleReads.from_trimmomatic(i, i.name) for i in folders]

	read_assembly.read_assembly(samples, parent_folder)


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


def main_pairwise_variant_calling():
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	pipeline_folder = checkdir(lipuma_folder / "pipeline_nanopore")
	reference_folder = lipuma_folder / "genomes" / "assembly_nanopore"

	reference_sc1360 = reference_folder / "SC1360Build" / "SC1360.polished.fasta"
	reference_sc1128 = reference_folder / "SC1128Build" / "SC1128.polished.fasta"
	reference_au0075 = reference_folder / "AU0075Build" / "AU0075.polished.fasta"

	sequence_folder = lipuma_folder / "genomes" / "reads" / "raw"
	samples = list()
	for sample_read_folder in sequence_folder.iterdir():
		try:
			sample = sampleio.SampleReads.from_folder(sample_read_folder)
		except:
			logger.warning(f"Could not collect the reads from folder {sample_read_folder}")
			continue
		samples.append(sample)

	sample_name_map_filename = lipuma_folder / "isolate_sample_map.old.txt"

	sample_name_map = dict()
	content = sample_name_map_filename.read_text()
	lines = content.split('\n')
	for line in lines:
		sample_id, sample_name = line.strip().split('\t')
		sample_name_map[sample_id] = sample_name

	sibling_pair_a_ids = [k for k, v in sample_name_map.items() if v.startswith('A')]
	sibling_pair_b_ids = [k for k, v in sample_name_map.items() if v.startswith('B')]
	sibling_pair_f_ids = [k for k, v in sample_name_map.items() if v.startswith('F')]

	sibling_pair_a_samples = [i for i in samples if i.name in sibling_pair_a_ids]
	sibling_pair_b_samples = [i for i in samples if i.name in sibling_pair_b_ids]
	sibling_pair_f_samples = [i for i in samples if i.name in sibling_pair_f_ids]

	assert len(sibling_pair_a_samples) == 25
	assert len(sibling_pair_b_samples) == 25
	assert len(sibling_pair_f_samples) == 18

	sibling_pair_a_folder = checkdir(pipeline_folder / "SC1360")
	sibling_pair_b_folder = checkdir(pipeline_folder / "SC1128")
	sibling_pair_f_folder = checkdir(pipeline_folder / "AU0075")

	sample_variant_calling(reference_sc1360, sibling_pair_a_samples, sibling_pair_a_folder)
	sample_variant_calling(reference_sc1128, sibling_pair_b_samples, sibling_pair_b_folder)
	sample_variant_calling(reference_au0075, sibling_pair_f_samples, sibling_pair_f_folder)


def main():
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	update_folder = checkdir(lipuma_folder / "2019-07-24-update")
	reference_folder = update_folder / "reference_samples"
	pipeline_folder = checkdir(update_folder / "pairwise_pipeline")

	references = [
		reference_folder / "AU1064" / "annotation" / "AU1064.gbk",
		reference_folder / "SC1360" / "annotation" / "SC1360.gbk",
		reference_folder / "SC1128" / "annotation" / "SC1128.gbk",
		reference_folder / "SC1145" / "annotation" / "SC1145.gbk",
		reference_folder / "AU1836" / "annotation" / "AU1836.gbk",
		reference_folder / "AU3415" / "annotation" / "AU3415.gbk",
		reference_folder / "AU0075" / "annotation" / "AU0075.gbk",
		reference_folder / "AU15033" / "annotation" / "AU15033.gbk",
	]

	sequence_folder = lipuma_folder / "genomes" / "reads" / "trimmedMajor"

	samples = list()
	for sample_read_folder in sequence_folder.iterdir():
		try:
			sample = sampleio.SampleReads.from_folder(sample_read_folder)
		except:
			logger.warning(f"Could not collect the reads from folder {sample_read_folder}")
			continue
		samples.append(sample)

	sample_name_map_filename = lipuma_folder / "isolate_sample_map.old.txt"
	sample_name_map = read_sample_map(sample_name_map_filename)

	sibling_pair_a_ids = [k for k, v in sample_name_map.items() if v.startswith('A')]
	sibling_pair_b_ids = [k for k, v in sample_name_map.items() if v.startswith('B')]
	sibling_pair_e_ids = [k for k, v in sample_name_map.items() if v.startswith('E')]
	sibling_pair_f_ids = [k for k, v in sample_name_map.items() if v.startswith('F')]

	sibling_pair_a_samples = [i for i in samples if i.name in sibling_pair_a_ids]
	sibling_pair_b_samples = [i for i in samples if i.name in sibling_pair_b_ids]
	sibling_pair_e_samples = [i for i in samples if i.name in sibling_pair_e_ids]
	sibling_pair_f_samples = [i for i in samples if i.name in sibling_pair_f_ids]

	assert len(sibling_pair_a_samples) == 25
	assert len(sibling_pair_b_samples) == 25
	assert len(sibling_pair_e_samples) == 27
	assert len(sibling_pair_f_samples) == 18

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


# def update_2019_07_24():
def main():
	""" Re runs asembly and analysis for newly trimmed samples."""
	lipuma_folder = Path.home() / "projects" / "lipuma"
	genomes_folder = lipuma_folder / "genomes"
	hi2424_prefix = genomes_folder / "reference" / "HI2424"
	isolate_map = lipuma_folder / "isolate_sample_map.old.txt"
	update_folder = checkdir(lipuma_folder / "2019-07-24-update")
	reference_folder = update_folder / "reference_samples"

	reference_sample_labels = ["AU0075", "AU1064", "AU1836", "AU3415", "AU15033", "SC1128", "SC1360", "SC1145"]
	reference_parent_pair = ["F", "A", "E", "E", "F", "B", "A", "B"]

	trimmed_reads_folder = lipuma_folder / "genomes" / "reads" / "trimmedMajor"  # stringent trimming
	trimmed_reads_samples = list(i for i in trimmed_reads_folder.iterdir() if i.is_dir())

	# First, assemble and annotate the references
	reference_output_folder = checkdir(update_folder / "reference_samples")
	reference_sample_folders = [i for i in trimmed_reads_samples if i.name in reference_sample_labels]
	reference_samples = [sampleio.SampleReads.from_trimmomatic(i, i.name) for i in reference_sample_folders]

	read_assembly.read_assembly(reference_samples, reference_output_folder)


def assembly_main():
	pass


if __name__ == "__main__":
	main()
