from pipelines.programs import fastqc


def test_fastqc(tmp_path, sample_reads):
	fastqc_workflow = fastqc.FastQC()
	output_folder = tmp_path / "output"
	output = fastqc_workflow.run(output_folder, *sample_reads.reads())

	assert output.exists()
