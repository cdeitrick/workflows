from pipelines.programs import trimmomatic


def test_trimmomatic(tmp_path, sample_reads):
	output_folder = tmp_path / "output"
	trimmomatic_workflow = trimmomatic.Trimmomatic()
	trimmomatic.systemio.command_runner.use_srun = False
	output = trimmomatic_workflow.run(sample_reads.forward, sample_reads.reverse, output_folder)

	assert output.exists()
