import sys
from pathlib import Path

import pytest

from pipelines.programs import shovill
from pipelines import programio


@pytest.fixture
def sample_output() -> shovill.ShovillOutput:
	contigs = SHOVILL_FOLDER / "contigs.fa"
	contigs_gfa = SHOVILL_FOLDER / "contigs.gfa"
	contigs_spades = SHOVILL_FOLDER / "spades.fasta"

	return programio.ShovillOutput("PA01", SHOVILL_FOLDER, contigs, contigs_gfa, contigs_spades)


# TODO: Make sure the ShovillOutput class can handle the case where pilon fails.

DATA_FOLDER = Path(__file__).parent / "data"
SHOVILL_FOLDER = DATA_FOLDER / "outputs" / "shovill"

sys.path.append("/home/cld100/anaconda3/envs/shovill/bin/")


def test_shovill(tmp_path, sample_reads):
	shovill_workflow = shovill.Shovill()
	output_folder = tmp_path / "output"
	output = shovill_workflow.run(sample_reads.forward, sample_reads.reverse, output_folder)

	assert output.exists()



def test_shovill_output_expected_without_sample_name(sample_output):
	result = programio.ShovillOutput.expected(SHOVILL_FOLDER)
	assert result == sample_output


def test_shovill_output_expected_with_sample_name(sample_output):
	result = programio.ShovillOutput.expected(SHOVILL_FOLDER)
	assert result == sample_output

	# Also test that the sample_name overrides the sample_name inferrence step.
	result = programio.ShovillOutput.expected(SHOVILL_FOLDER, "PA01test")
	sample_output.name = "PA01test"
	assert result == sample_output


def test_shovill_output_from_folder_without_sample_name(sample_output):
	result = programio.ShovillOutput.from_folder(SHOVILL_FOLDER)

	assert result == sample_output


def test_shovill_output_from_folder_with_sample_name(sample_output):
	result = programio.ShovillOutput.from_folder(SHOVILL_FOLDER)
	assert result == sample_output

	# Also test that the sample_name overrides the sample_name inferrence step.
	result = programio.ShovillOutput.from_folder(SHOVILL_FOLDER, "PA01test")
	sample_output.name = "PA01test"
	assert result == sample_output
