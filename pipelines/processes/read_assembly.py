from pathlib import Path
from pipelines.programs import trimmomatic, fastqc, shovill
from pipelines import systemio, sampleio
from typing import Optional, Dict, Any, List

def stringent_parameters()->Dict[str,Any]:
	parameters = {
		'minimum': 70,
		'leading': 20,
		'trailing': 20
	}
	return parameters


def read_assembly(samples:List[sampleio.SampleReads], parent_folder:Path):
	trimmomatic_workflow = trimmomatic.Trimmomatic(**stringent_parameters())
	shovill_workflow = shovill.Shovill()

	for sample in samples:
		sample_folder = parent_folder / sample.name
		trimmomatic_folder = sample_folder / "trimmomatic"
		shovill_folder = sample_folder / "shovill"
		trimmomatic_output = trimmomatic_workflow.run(sample.forward, sample.reverse, trimmomatic_folder)
		shovill_workflow.run(trimmomatic_output.forward, trimmomatic_output.reverse, shovill_folder)