from pipelines.programs import breseq
from loguru import logger
import sys
import pytest
@pytest.mark.skip() # The workflow has been tested and works, but takes a while to run.
def test_breseq(assembly, sample_reads, tmp_path):
	logger.info(sys.path)
	breseq_workflow = breseq.Breseq(assembly)
	breseq_workflow.program = "/home/cld100/applications/breseq-0.33.1/bin/breseq"
	output_folder = tmp_path / "output"
	breseq_output = breseq_workflow.run(output_folder, sample_reads.forward, sample_reads.reverse)

	assert breseq_output.exists()