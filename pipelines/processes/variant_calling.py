from pathlib import Path
from typing import List, Union

from loguru import logger

from pipelines import programio, sampleio, systemio, utilities
from pipelines.programs import breseq


def sample_variant_calling(reference: Path, samples: List[sampleio.SampleReads], project_folder: Path):
	"""
		Performs simple variant calling between the supplied reference and the given samples.
	Parameters
	----------
	reference: Path
		The sample to use for the project
	samples: List[sampleio.SampleReads
		Contsins the source reads for variant calling. Trimming is not performmed at this stage.
	project_folder: Path
		The folder to use for the overall project.

	Returns
	-------

	"""
	# First validate the input parameters
	cancel = not utilities.verify_file_exists(reference)
	cancel = cancel or not sampleio.verify_samples(samples)

	if cancel:
		message = "Something went wrong when validating the variant calling parameters!"
		raise ValueError(message)

	# Set up the environment
	utilities.checkdir(project_folder)

	systemio.command_runner.set_command_log(project_folder / "commandlog_variant_calling.sh")
	systemio.command_runner.write_command_to_commandlog(['module', 'load', 'breseq'])

	breseq_workflow = breseq.Breseq(reference)
	breseq_workflow.test()

	results = list()
	for index, sample in enumerate(samples):
		logger.info(f"Running variant calling on sample {index} of {len(samples)}: {sample.name}")
		sample_folder = utilities.checkdir(project_folder / sample.name)
		breseq_folder = sample_folder / "breseq"

		result = breseq_workflow.run(breseq_folder, sample.forward, sample.reverse)
		results.append(result)
	return results


