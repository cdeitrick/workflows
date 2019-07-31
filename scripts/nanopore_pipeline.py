import sys
from pathlib import Path
from typing import Dict
from loguru import logger

from pipelines import processes, sampleio

directory = Path(__file__).parent.parent.parent.absolute() # so pipelines` is visible
sys.path.append(str(directory))


def checkdir(path: Path) -> Path:
	path = Path(path)
	if not path.exists():
		path.mkdir()
	return path

def read_sample_name_map(filename:Path)->Dict[str,str]:
	sample_name_map = dict()
	content = filename.read_text()
	lines = content.split('\n')
	for line in lines:
		sample_id, sample_name = line.strip().split('\t')
		sample_name_map[sample_id] = sample_name
	return sample_name_map
def main():
	lipuma_folder = Path("/home/cld100/projects/lipuma")
	update_folder = lipuma_folder / "201907-24-update"
	pipeline_folder = checkdir(update_folder / "pipeline_nanopore")

	reference_folder = lipuma_folder / "genomes" / "assembly" / "assembly_nanopore"

	reference_sc1360 = reference_folder / "SC1360" / "SC1360.polished.fasta"
	reference_sc1128 = reference_folder / "SC1128" / "SC1128.polished.fasta"
	reference_au0075 = reference_folder / "AU0075" / "AU0075.polished.fasta"

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

	sample_name_map = read_sample_name_map(sample_name_map_filename)

	sibling_pair_a_ids = [k for k, v in sample_name_map.items() if (v.startswith('A0') or v.startswith('A1'))]
	sibling_pair_b_ids = [k for k, v in sample_name_map.items() if (v.startswith('B0') or v.startswith('B1'))]
	sibling_pair_f_ids = [k for k, v in sample_name_map.items() if (v.startswith('F0') or v.startswith('F1'))]

	sibling_pair_a_samples = [i for i in samples if i.name in sibling_pair_a_ids]
	sibling_pair_b_samples = [i for i in samples if i.name in sibling_pair_b_ids]
	sibling_pair_f_samples = [i for i in samples if i.name in sibling_pair_f_ids]

	assert len(sibling_pair_a_samples) == 25
	assert len(sibling_pair_b_samples) == 25
	assert len(sibling_pair_f_samples) == 18

	sibling_pair_a_folder = checkdir(pipeline_folder / "SC1360")
	sibling_pair_b_folder = checkdir(pipeline_folder / "SC1128")
	sibling_pair_f_folder = checkdir(pipeline_folder / "AU0075")

	processes.variant_calling.sample_variant_calling(reference_sc1360, sibling_pair_a_samples, sibling_pair_a_folder)
	processes.variant_calling.sample_variant_calling(reference_sc1128, sibling_pair_b_samples, sibling_pair_b_folder)
	processes.variant_calling.sample_variant_calling(reference_au0075, sibling_pair_f_samples, sibling_pair_f_folder)

if __name__ == "__main__":
	main()