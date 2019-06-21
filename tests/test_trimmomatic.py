from pathlib import Path
import pytest
from workflows.programs import trimmomatic
from workflows import sampleio

def test_trimmomatic(tmp_path, sample_reads):
	output_folder = tmp_path / "output"
	trimmomatic_workflow = trimmomatic.Trimmomatic()
	trimmomatic_workflow.program = "java -jar /home/cld100/applications/Trimmomatic-0.39/trimmomatic-0.39.jar"
	output = trimmomatic_workflow.run(sample_reads.forward, sample_reads.reverse, output_folder)

	assert output.exists()


