from pathlib import Path
from typing import List, Union

from loguru import logger

from pipelines import programio, sampleio, systemio, utilities
from pipelines.programs import shovill, trimmomatic
from pipelines.utilities import checkdir


class AssemblyWorkflow:
	def __init__(self, project_folder: Path):
		systemio.command_runner.set_command_log(project_folder / "commandlog_trimming.sh")
		systemio.command_runner.write_command_to_commandlog(['module', 'load', 'trimmomatic'])
		systemio.command_runner.write_command_to_commandlog(['module', 'load', 'shovill'])

		self.trimmomatic_workflow = trimmomatic.Trimmomatic(stringent = True)
		self.shovill_workflow = shovill.Shovill()

	def run(self, samples: List[Union[sampleio.SampleReads, programio.TrimmomaticOutput]], project_folder: Path) -> List[programio.ShovillOutput]:
		logger.info(f"Assembling {len(samples)} samples...")
		cancel = not sampleio.verify_samples(samples)

		if cancel:
			message = "Something went wrong when validating the variant calling parameters!"
			raise ValueError(message)

		utilities.checkdir(project_folder)

		output_files = list()
		for index, sample in enumerate(samples, start = 1):
			logger.info(f"Assembling sample {index} of {len(samples)}: {sample.name}")
			sample_folder = checkdir(project_folder / sample.name)
			result = self.assemble_sample(sample, sample_folder)
			output_files.append(result)
		return output_files

	def assemble_sample(self, sample: Union[sampleio.SampleReads, programio.TrimmomaticOutput], sample_folder: Path) -> programio.ShovillOutput:
		trimmomatic_folder = checkdir(sample_folder / "trimmomatic")
		shovill_folder = checkdir(sample_folder / "shovill")

		if isinstance(sample, sampleio.SampleReads):
			trimmomatic_output = self.trimmomatic_workflow.run(sample.forward, sample.reverse, trimmomatic_folder)
		else:
			logger.info(f"\t'{sample.name}' is already trimmed. Skipping...")
			trimmomatic_output = sample

		result = self.shovill_workflow.run(trimmomatic_output.forward, trimmomatic_output.reverse, shovill_folder, sample_folder.name)
		return result


def read_assembly(samples: List[Union[sampleio.SampleReads, programio.TrimmomaticOutput]], project_folder: Path) -> List[programio.ShovillOutput]:
	workflow = AssemblyWorkflow(project_folder)
	results = workflow.run(samples, project_folder)
	return results
