from pathlib import Path
from workflows import systemio, sampleio
from workflows.programs import trimmomatic, breseq
from typing import List
from loguru import logger
def sample_variant_calling(reference:Path, samples: List[sampleio.SampleReads], parent_folder:Path):
	systemio.command_runner.set_command_log(parent_folder / "variant_calling_commands.sh")
	trimmomatic_workflow = trimmomatic.Trimmomatic()
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

