from pathlib import Path

from loguru import logger

from workflows import sampleio
from workflows.processes.variant_calling import sample_variant_calling

if __name__ == "__main__":
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	pipeline_folder = lipuma_folder / "pipeline_nanopore"
	reference_folder = lipuma_folder / "reads" / "nanopore"

	reference_sc1128 = reference_folder / "SC1128Build" / "SC1128.fasta"
	reference_sc1360 = reference_folder / "SC1360Build" / "SC1360.fasta"
	reference_au0075 = reference_folder / "AU0075Build" / "AU0075.fasta"

	sequence_folder = lipuma_folder / "reads"
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

	sibling_pair_a_folder = pipeline_folder / "SC1360"
	sibling_pair_b_folder = pipeline_folder / "SC1128"
	sibling_pair_f_folder = pipeline_folder / "AU0075"

	sample_variant_calling(reference_sc1360, sibling_pair_a_samples, sibling_pair_a_folder)
	sample_variant_calling(reference_sc1128, sibling_pair_b_samples, sibling_pair_b_folder)
	sample_variant_calling(reference_au0075, sibling_pair_f_samples, sibling_pair_f_folder)
