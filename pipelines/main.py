"""
The entry point for scripts using the piplelines.
"""
from pathlib import Path

from loguru import logger

from pipelines import sampleio
from pipelines.processes.variant_calling import sample_variant_calling
def checkdir(path:Path)->Path:
	path = Path(path)
	if not path.exists():
		path.mkdir()
	return path

def main():

	lipuma_folder = Path("/home/cld100/projects/lipuma")

	# /home/cld100/projects/lipuma/pairwise_pipeline_shovill/AU1064/AU3827/breseq_output

	parent_folder = lipuma_folder / "pairwise_pipeline_shovill"
	reference_folder = lipuma_folder / "genomes" / "assembly" / "assembly_shovill_annotated"
	sample_folder = lipuma_folder / "genomes" / "reads" / "raw"

	au1064 = reference_folder / "AU1064" / "AU1064.gff"
	sc1360 = reference_folder / "SC1360" / "SC1360.gff"

	sc1128 = reference_folder / "SC1128" / "SC1128.gff"
	sc1145 = reference_folder / "SC1145" / "SC1145.gff"

	au1836 = reference_folder / "AU1836" / "AU1836.gff"
	au3415 = reference_folder / "AU3415" / "AU3415.gff"

	patient_pair_a_samples = [sampleio.SampleReads.from_folder(sample_folder / "AU3827B")]
	patient_pair_b_samples = [sampleio.SampleReads.from_folder(sample_folder / "AU3740B")]
	patient_pair_e_samples = [sample_folder / "AU3415B", sample_folder / "AU3416B", sample_folder / "AU6936B"]
	patient_pair_e_samples = [sampleio.SampleReads.from_folder(i) for i in patient_pair_e_samples]
	#sample_variant_calling(reference_sc1360, sibling_pair_a_samples, sibling_pair_a_folder)

	sample_variant_calling(au1064, patient_pair_a_samples, checkdir(parent_folder / "AU1064"))
	sample_variant_calling(sc1360, patient_pair_a_samples, checkdir(parent_folder / "SC1360"))
	sample_variant_calling(sc1128, patient_pair_b_samples, checkdir(parent_folder / "SC1128"))
	sample_variant_calling(sc1145, patient_pair_b_samples, checkdir(parent_folder / "SC1145"))
	sample_variant_calling(au1836, patient_pair_e_samples, checkdir(parent_folder / "AU1836"))
	sample_variant_calling(au3415, patient_pair_e_samples, checkdir(parent_folder / "AU3415"))

def main_nanopore():
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	pipeline_folder = checkdir(lipuma_folder / "pipeline_nanopore")
	reference_folder = lipuma_folder /"genomes" / "assembly_nanopore"

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
if __name__ == "__main__":
	main_pairwise_pipeline()
