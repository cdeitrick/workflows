import pytest
from pipelines import sampleio
from pathlib import Path
from loguru import logger
def checkdir(path)->Path:
	if not path.exists():
		path.mkdir()
	return path
@pytest.fixture
def sample_folder(tmp_path)->Path:
	name = "AB1234"
	sample_folder = tmp_path / name
	if not sample_folder.exists(): sample_folder.mkdir()

	forward = sample_folder / f"{name}_R1_001.fastq"
	reverse = sample_folder / f"{name}_R2_001.fastq"

	forward.touch()
	reverse.touch()

	return sample_folder

@pytest.fixture
def folder_of_samples(tmp_path)->Path:
	""" A folder of samples"""
	parent_folder = checkdir(tmp_path / "samples")

	sample_a_name = "AB1234"
	sample_b_name = "CD5678"
	sample_c_name = "EF9012"

	sample_a_folder = checkdir(parent_folder / sample_a_name)
	sample_b_folder = checkdir(parent_folder / sample_b_name)
	sample_c_folder = checkdir(parent_folder / sample_c_name)

	(sample_a_folder / f"{sample_a_name}_R1_001.fastq").touch()
	(sample_a_folder / f"{sample_a_name}_R2_001.fastq").touch()

	(sample_b_folder / f"{sample_b_name}_R1_001.fastq").touch()
	(sample_b_folder / f"{sample_b_name}_R2_001.fastq").touch()

	(sample_c_folder / f"{sample_c_name}_R1_001.fastq").touch()
	(sample_c_folder / f"{sample_c_name}_R2_001.fastq").touch()

	# Add an extra folder that should be ignored.
	checkdir(parent_folder / "other_folder")

	# Add a file that should be ignored
	(parent_folder / "ignored_file.txt").touch()

	return parent_folder

def test_sample_reads_from_folder(sample_folder):
	result = sampleio.SampleReads.from_folder(sample_folder)

	assert result.forward.exists()
	assert result.reverse.exists()

def test_get_multiple_sample_reads_from_folder(folder_of_samples):
	result = sampleio.get_samples_from_folder(folder_of_samples)

	assert result[0].exists()
	assert result[1].exists()
	assert result[2].exists()

@pytest.mark.parametrize("value,expected",
[
	("M64_123_S50_R1_001.fastq", "M64_123"),
	("/home/cld100/projects/mcbride/McBrideLab/051919_52/630_dErm_S52_R1_001.fastq.gz", "630_dErm")
]
)
def test_get_sample_name_from_reads(value,expected):
	result = sampleio.get_name_from_reads(value)
	assert result == expected