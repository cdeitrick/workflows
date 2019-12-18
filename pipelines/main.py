"""
The entry point for scripts using the piplelines.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from loguru import logger

#from pipelines import sampleio
#from pipelines.processes import read_assembly
#from pipelines.processes.variant_calling import sample_variant_calling
#from pipelines import programio

def _shelly_get_sample_reads_from_folder(folder:Path)->Optional[Tuple[Path,Path]]:
	reads = list(folder.iterdir())
	try:
		read_forward = [i for i in reads if i.stem.endswith('1')][0]
		read_reverse = [i for i in reads if i.stem.endswith('2')][0]
	except IndexError:
		return None
	return read_forward, read_reverse

def collect_samples_from_folder(folder:Path)->List[Dict[str,Union[str,Path]]]:
	result = list()
	for subfolder in folder.iterdir():
		reads = _shelly_get_sample_reads_from_folder(subfolder)

		if reads:
			data = {
				'sampleName': subfolder.name,
				'readForward': reads[0],
				'readReverse': reads[1]
			}
			result.append(data)
		else:
			message = f"Cannot find the reads for sample {folder.name}"
			logger.warning(message)
	return result

def main_shelly():
	logger.info(" Running the large dataset of samples.")

	project_folder = Path.home() / "projects" / "shelly"

	bioproject_folder_left = project_folder / "bioproject-PRJNA407467"
	bioproject_folder_right = project_folder / "bioproject-PRJNA499085"

	bioproject_samples_folder_left = bioproject_folder_left / "samples"
	bioproject_samples_folder_right = bioproject_folder_right / "samples"

	bioproject_samples_left = collect_samples_from_folder(bioproject_samples_folder_left)
	bioproject_samples_right = collect_samples_from_folder(bioproject_samples_folder_right)

	project_samples = bioproject_samples_left + bioproject_samples_right

	import csv
	outputpath = project_folder / "samples.tsv"
	with outputpath.open('w') as output:
		writer = csv.DictWriter(output, fieldnames = ["sampleName", "readForward", "readReverse"])
		writer.writeheader()
		writer.writerows(project_samples)