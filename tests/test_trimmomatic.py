from pathlib import Path
import pytest
from pipelines.programs import trimmomatic
from pipelines import sampleio

def test_trimmomatic(tmp_path, sample_reads):
	output_folder = tmp_path / "output"
	trimmomatic_workflow = trimmomatic.Trimmomatic()
	output = trimmomatic_workflow.run(sample_reads.forward, sample_reads.reverse, output_folder)

	assert output.exists()


