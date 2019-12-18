
from pathlib import Path
from pipelines.programs import trimmomatic
from pipelines import programio
from pipelines import sampleio
from typing import List
from loguru import logger

def trim(samples:List[sampleio.SampleReads], project_folder:Path, stringent:bool = False)->List[programio.TrimmomaticOutput]:
	cancel = not sampleio.verify_samples(samples)

	if cancel:
		message = "Something went wrong when validating the variant calling parameters!"
		raise ValueError(message)

	trimmomatic_workflow = trimmomatic.Trimmomatic(stringent = stringent)
	output_files = list()
	for index, sample in enumerate(samples):
		logger.info(f"Trimming sample {index} of {len(samples)}: {sample.name}")

		trimmomatic_output = trimmomatic_workflow.run(sample.forward, sample.reverse, project_folder / sample.name, sample.name)
		output_files.append(trimmomatic_output)
	return output_files