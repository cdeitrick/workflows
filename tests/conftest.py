from pathlib import Path

import pytest

from pipelines import sampleio, systemio

DATA_FOLDER = Path(__file__).parent / "data"


@pytest.fixture
def sample_reads(tmp_path) -> sampleio.SampleReads:
	name = "AU1234"
	sample_folder = tmp_path / name
	if not sample_folder.exists(): sample_folder.mkdir()

	forward = sample_folder / f"{name}_S0_R1_001.fastq"
	reverse = sample_folder / f"{name}_S0_R2_001.fastq"

	forward_source = DATA_FOLDER /"inputs" / "reads" / f"{name}_S0_R1_001.fastq"
	reverse_source = DATA_FOLDER /"inputs" / "reads" / f"{name}_S0_R2_001.fastq"
	forward.write_bytes(forward_source.read_bytes())
	reverse.write_bytes(reverse_source.read_bytes())

	return sampleio.SampleReads.from_folder(sample_folder)


def trimmed_reads() -> Path:
	pass


@pytest.fixture
def assembly() -> Path:
	return DATA_FOLDER / "assembly.fna"


@pytest.fixture
def command_runner() -> systemio.CommandRunner:
	return systemio.CommandRunner(srun = False)


def copy_folder(source_folder, target_folder):
	""" Copies all files in a folder to the target without copying the contents."""

	for item in source_folder.iterdir():
		if item.is_folder(): continue
		target = target_folder / item.name
		target.touch()
