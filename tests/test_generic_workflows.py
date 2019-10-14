from pathlib import Path

import pytest

from pipelines import utilities, programio, systemio
from pipelines.processes import generic
systemio.command_runner.use_srun = False # Disable srun since it is not installed on this system
DATA_FOLDER = Path(__file__).parent / "data"


@pytest.fixture
def project_folder(tmp_path) -> Path:
	f = utilities.checkdir(tmp_path / "project")
	return f


@pytest.fixture
def reads_raw(project_folder) -> Path:
	source_folder = DATA_FOLDER / "inputs" / "reads"
	destination_folder = utilities.checkdir(project_folder / "reads")
	utilities.copydir(source_folder, destination_folder)
	return destination_folder


@pytest.fixture
def reads_trimmed(project_folder) -> Path:
	source_folder = DATA_FOLDER / "outputs" / "trimmomatic"
	destination_folder = utilities.checkdir(project_folder / "reads")
	utilities.copydir(source_folder, destination_folder)
	return destination_folder


@pytest.fixture
def generic_workflow(project_folder) -> generic.GenericVariantCalling:
	return generic.GenericVariantCalling(project_folder)


def test_process_reference_from_assembly(generic_workflow):
	assembly_filename = DATA_FOLDER / "inputs" / "AU1054 GENBANK" / "GCA_000014085.1_ASM1408v1_genomic.fna"
	result = generic_workflow.process_reference(assembly_filename)
	assert result == assembly_filename


def test_process_reference_from_read_folder_raw(generic_workflow, reads_raw):
	expected = generic_workflow.project_folder / "AU1234" / "shovill" / "contigs.fa"
	result = generic_workflow.process_reference(reads_raw)

	assert result == expected


def test_process_reference_from_read_folder_trimmed(generic_workflow, reads_trimmed):
	expected = generic_workflow.project_folder / "PA01" / "shovill" / "contigs.fa"
	result = generic_workflow.process_reference(reads_trimmed)
	assert result == expected


def test_process_reference_from_trimmomatic_output(generic_workflow, reads_trimmed):
	reads = programio.TrimmomaticOutput.from_folder(reads_trimmed)
	result = generic_workflow.process_reference(reads)
	expected = generic_workflow.project_folder / "PA01" / "shovill" / "contigs.fa"

	assert result == expected

