import pytest
from pipelines.programs import shovill
import sys
sys.path.append("/home/cld100/anaconda3/envs/shovill/bin/")
def test_shovill(tmp_path, sample_reads):
	shovill_workflow = shovill.Shovill()
	output_folder = tmp_path / "output"
	output = shovill_workflow.run(sample_reads.forward, sample_reads.reverse, output_folder)

	assert output.exists()

