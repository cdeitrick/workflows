from pathlib import Path

from pipelines import systemio, sampleio
from pipelines.programs import trimmomatic, breseq

from typing import List
from loguru import logger
def sample_variant_calling(reference:Path, samples: List[sampleio.SampleReads], parent_folder:Path):
	cancel = False
	# First validate the input parameters
	if not reference.exists():
		logger.critical(f"The reference file does not exist: {reference}")
		cancel = True
	if not parent_folder.exists():
		logger.critical(f"The parent folder does not exist: {parent_folder}")
		cancel = True

	for sample in samples:
		if not sample.forward.exists() or not sample.reverse.exists():
			logger.critical(f"The read files for sample {sample.name} do not exist")
			cancel = True

	if cancel:
		message = "Something went wrong when validating the variant calling parameters!"
		raise ValueError(message)

	# Set up the environment
	systemio.command_runner.set_command_log(parent_folder / "variant_calling_commands.sh")
	trimmomatic_workflow = trimmomatic.Trimmomatic(stringent = True)
	trimmomatic_workflow.test()
	breseq_workflow = breseq.Breseq(reference)
	breseq_workflow.test()

	sampleio.validate_samples(samples)

	for index, sample in enumerate(samples):
		logger.info(f"Running variant calling on sample {index} of {len(samples)}: {sample.name}")
		sample_folder = systemio.checkdir(parent_folder / sample.name)
		trimmomatic_folder = sample_folder / "trimmomatic"
		breseq_folder = sample_folder / "breseq"
		trimmomatic_output = trimmomatic_workflow.run(sample.forward, sample.reverse, trimmomatic_folder)
		breseq_workflow.run(breseq_folder, trimmomatic_output.forward, trimmomatic_output.reverse)


