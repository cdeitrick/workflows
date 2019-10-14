from pathlib import Path

import pytest

from pipelines import sampleio, utilities

DATA_FOLDER = Path(__file__).parent / "data"
TRIMMOMATIC_FOLDER = DATA_FOLDER / "outputs" / "trimmomatic"
READ_FILENAMES = [
	Path("AU1234_S0_R1_001.fastq"),
	Path("AU1234_S0_R2_001.fastq"),
	Path("PA01.forward.trimmed.paired.fastq"),
	Path("PA01.forward.trimmed.unpaired.fastq"),
	Path("PA01.reverse.trimmed.paired.fastq"),
	Path("PA01.reverse.trimmed.unpaired.fastq")
]


@pytest.fixture
def rawsample(tmp_path) -> sampleio.SampleReads:
	source_folder = DATA_FOLDER / "inputs" / "reads"

	source_forward = source_folder / "AU1234_S0_R1_001.fastq"
	source_reverse = source_folder / "AU1234_S0_R2_001.fastq"

	parent = tmp_path / "reads"
	parent.mkdir()

	target_forward = parent / source_forward.name
	target_reverse = parent / source_reverse.name

	# Since none of the utilities care about the actual contents of the read files,
	# Only generate empty files to save space.
	target_forward.touch()
	target_reverse.touch()

	sample = sampleio.SampleReads("AU1234", target_forward, target_reverse, parent)
	return sample


@pytest.fixture
def temporary_folder(tmp_path) -> Path:
	temp_folder = tmp_path / "folder"
	temp_folder.mkdir()
	return temp_folder


def test_checkdir_with_path(temporary_folder):
	target_directory = temporary_folder / "target"
	# Make sure the target doesn't already exist
	assert not target_directory.exists()
	utilities.checkdir(target_directory)
	assert target_directory.exists()


def test_checkdir_with_str(temporary_folder):
	target_directory = temporary_folder / "target"
	# Make sure the target doesn't already exist
	assert not target_directory.exists()
	target_directory_string = str(target_directory)
	utilities.checkdir(target_directory_string)
	assert target_directory.exists()


# TODO: Include trimmed reads with this.
@pytest.mark.parametrize(
	"filename, expected",
	zip(
		READ_FILENAMES + [str(i) for i in READ_FILENAMES],
		[True, False, True, False, False, False] * 2  # Should append a copy of the list.
	)
)
def test_is_forward_read(filename, expected):
	result = utilities.is_forward_read(filename)
	assert result == expected


@pytest.mark.parametrize(
	"filename, expected",
	zip(
		READ_FILENAMES + [str(i) for i in READ_FILENAMES],
		[False, True, False, False, True, False] * 2
	)
)
def test_is_reverse_read(filename, expected):
	result = utilities.is_reverse_read(filename)
	assert result == expected


@pytest.mark.parametrize("filename, expected", zip(READ_FILENAMES, (["AU1234"] * 2 + ["PA01"] * 4) * 2))
def test_get_name_from_reads(filename, expected):
	result = utilities.get_name_from_reads(filename)
	assert result == expected


def test_get_reads_from_folder(rawsample):
	forward, reverse = utilities.get_reads_from_folder(rawsample.folder)

	assert forward == rawsample.forward
	assert reverse == rawsample.reverse


@pytest.mark.parametrize(
	"left, right, expected",
	[
		("PA01.forward", "PA01.reverse", "PA01")
	]
)
def test_get_longest_substring(left, right, expected):
	result = utilities.get_longest_substring(left, right)
	assert result == expected


@pytest.mark.parametrize(
	"folder, expected",
	[
		(DATA_FOLDER / "inputs" / "reads", "reads"),
		(DATA_FOLDER / "outputs" / "trimmomatic", "trimmomatic"),
		# (DATA_FOLDER / "", "spades"),
		(DATA_FOLDER / "outputs" / "shovill", "shovill"),
		(DATA_FOLDER / "outputs" / "breseq", "breseq"),
		(DATA_FOLDER / "outputs" / "prokka", "prokka"),
		(DATA_FOLDER / "inputs" / "AU1054 GENBANK", "genbank"),
		(DATA_FOLDER / "inputs" / "AU1054 REFSEQ", "refseq")
	]
)
def test_get_folder_type(folder, expected):
	result = utilities.get_folder_type(folder)
	assert result == expected
