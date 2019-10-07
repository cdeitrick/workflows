from pathlib import Path
from pipelines.programs import trimmomatic, shovill
from pipelines.utilities import checkdir
from pipelines import sampleio
from typing import List
from loguru import logger

def read_assembly(samples:List[sampleio.SampleReads], parent_folder:Path, stringent:bool = False)->List[shovill.ShovillOutput]:
	logger.info(f"Assembling {len(samples)} samples...")
	cancel = False

	if not parent_folder.exists():
		try:
			parent_folder.mkdir()
		except FileNotFoundError:
			logger.critical(f"The parent folder does not exist and cannot be created: {parent_folder}")
			cancel = True

	for sample in samples:
		if not sample.forward.exists() or not sample.reverse.exists():
			logger.critical(f"The read files for sample {sample.name} do not exist")
			cancel = True

	if cancel:
		message = "Something went wrong when validating the variant calling parameters!"
		raise ValueError(message)

	trimmomatic_workflow = trimmomatic.Trimmomatic(stringent = True)
	shovill_workflow = shovill.Shovill()
	output_files = list()
	for index, sample in enumerate(samples, start = 1):
		logger.info(f"Assembling sample {index} of {len(samples)}: {sample.name}")

		sample_folder = checkdir(parent_folder / sample.name)
		trimmomatic_folder = sample_folder / "trimmomatic"
		shovill_folder = checkdir(sample_folder / "shovill")

		if not sample.is_trimmed:
			trimmomatic_output = trimmomatic_workflow.run(sample.forward, sample.reverse, trimmomatic_folder)
		else:
			logger.info(f"\t'{sample.name}' is already trimmed. Skipping...")
			trimmomatic_output = sample

		result = shovill_workflow.run(trimmomatic_output.forward, trimmomatic_output.reverse, shovill_folder)
		output_files.append(result)
	return output_files