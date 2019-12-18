"""
The entry point for scripts using the piplelines.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from loguru import logger

from pipelines import sampleio
#from pipelines.processes import read_assembly
from pipelines.processes.variant_calling import sample_variant_calling
from pipelines.processes.read_trimming import trim
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
			message = f"Cannot find the reads for sample {subfolder.name} ('{subfolder.absolute()}')"
			logger.warning(message)
	return result

def main_shelly():
	logger.info(" Running the large dataset of samples.")

	project_folder = Path.home() / "projects" / "shelly"
	table_filename = project_folder / "samples.tsv"

	reference = Path()
	samples = sampleio.get_samples_from_table(table_filename)
	# Trim the reads
	trimmed_output = trim(samples, project_folder)
	trimmed_samples = [i.as_sample() for i in trimmed_output]
	# Call variants
	sample_variant_calling(reference, trimmed_samples, project_folder, ispop = True)