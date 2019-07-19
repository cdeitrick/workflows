
from pathlib import Path
from pipelines.programs import trimmomatic, shovill
from pipelines import sampleio
from typing import List
from loguru import logger

def trim(samples:List[sampleio.SampleReads], parent_folder:Path, stringent:bool = False):
	cancel = False
	for sample in samples:
		if not sample.forward.exists() or not sample.reverse.exists():
			logger.critical(f"The read files for sample {sample.name} do not exist")
			cancel = True

	if cancel:
		message = "Something went wrong when validating the variant calling parameters!"
		raise ValueError(message)


	trimmomatic_workflow = trimmomatic.Trimmomatic(stringent = stringent)

	for index, sample in enumerate(samples):
		logger.info(f"Trimming sample {index} of {len(samples)}: {sample.name}")

		trimmomatic_workflow.run(sample.forward, sample.reverse, parent_folder / sample.name)