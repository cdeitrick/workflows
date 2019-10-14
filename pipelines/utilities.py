from pathlib import Path
from typing import Optional, Tuple, Union

from loguru import logger


def checkdir(path: Union[str, Path]) -> Path:
	path = Path(path)
	if not path.exists():
		try:
			path.mkdir()
		except FileNotFoundError as exception:
			logger.critical(f"Cannot create '{path}'")
			logger.critical(f"\t{path.parent.exists()} -> {path.parent}")
	return path


def is_forward_read(filename: Union[str, Path]) -> bool:
	if isinstance(filename, Path):
		stem = filename.stem
	else:
		stem = filename
	if 'R1' in stem or ('forward' in stem and 'unpaired' not in stem):
		return True
	if '1P' in stem:
		return True
	return False


def is_reverse_read(filename: Union[str, Path]) -> bool:
	if isinstance(filename, Path):
		stem = filename.stem
	else:
		stem = filename
	if 'R2' in stem or ('reverse' in stem and 'unpaired' not in stem):
		return True
	if '2P' in filename.stem:
		return True
	return False


def get_name_from_reads(path: Union[str, Path]) -> Optional[str]:
	""" Gets the name of a sample from the filename of one of the fastq files."""
	if isinstance(path, str):
		path = Path(path)
	name = path.stem
	# If the path refers to a read file, only the first part is useful.
	if 'R1' in name or 'R2' in name:
		name = name.split('_')[:-3]
		sample_name = "_".join(name)

	elif 'forward' in name or 'reverse' in name:
		# Probably trimmed
		sample_name, *_ = name.partition('.')
	else:
		sample_name = None
	return sample_name


def get_reads_from_folder(folder: Path) -> Tuple[Path, Path]:
	"""
		Attempts to find the `forward` and `reverse` reads in a folder.
	Parameters
	----------
	folder: Path
		The folder to search in. May be either the raw sample read folder or a folder
		with trimmed reads.
	Raises
	------
	FileNotFoundError: Cannot locate either the forward or reverse files.
	"""
	candidates = list(i for i in folder.iterdir() if (i.suffix == '.fastq' or i.suffix == ''))
	if not candidates:
		logger.warning(
			f"The files might be gzipped. While *most* programs can still use the compressed files, not all can, so uncompress just in case.")
		logger.warning(f"This will have to be done manually for now.")

	try:
		forward = [i for i in candidates if is_forward_read(i)][0]
		reverse = [i for i in candidates if is_reverse_read(i)][0]
	except IndexError:
		message = f"Could not locate the reads in folder (exists = {folder.exists()}): '{folder}'"
		if folder.exists():
			logger.debug(f"Folder contents:")
			for i in folder.iterdir():
				logger.debug(f"\t{i}")
		raise FileNotFoundError(message)
	return forward, reverse


def verify_file_exists(filename: Path) -> bool:
	if not filename.exists():
		logger.critical(f"The file does not exist: {filename}")
		return False
	return True


def get_longest_substring(left: str, right: str) -> str:
	# Very dirty implementation
	string = list()
	for i, j in zip(left, right):
		if i == j:
			string.append(i)
		else:
			break
	substring = "".join(string)
	if substring.endswith('.'):
		substring = substring[:-1]
	return substring


# noinspection PyStatementEffect
def get_folder_type(folder: Path, silent: bool = False) -> Optional[str]:
	""" Returns the name of the programs that presumably created the folder.
		Returns
		-------
		- None: The type of folder cannot be determined with the current tests and `silent` is True
		- `reads`: A folder with the forward and reverse reads from the sequencer.
		- `trimmomatic`: A folder produced by trimmomatic containing trimmed reads.
		- `spades': A folder with the output from the spades assembler
		- `shovill`: A folder with the output from the shovill assembler
		- `breseq`: A folder with the output from breseq.
		- `prokka`: A folder with the output form prokka.
		- `refseq`: A folder with assembly file from refseq.
		- `genbank`: A folder with assembly files from genbank.
	"""

	# Test if it is a folder with only the raw reads from the sequencer.
	try:
		[i for i in folder.iterdir() if 'R1' in i.name][0]
		return 'reads'
	except IndexError:
		# The sequencer generally uses 'R1' and 'R2' to distinguish between forward and reverse reads.
		# If the forward read cannot be found in this folder, it it not a 'reads' folder.
		pass

	# Test if it is a folder with trimmed reads from Trimmomatic.

	# The filenames can be automatically generated or manually generated. Make sure this can handle both cases.
	# Test if the filenames were automatically generated.
	default_result = sum(i.match("*[12][PU][.]*") for i in folder.iterdir()) == 4

	# Test if the filenames were manually generated, but still from Trimmomatic
	# For now, just test if the files were generated from the trimmomatic setup used in the workflows.
	try:
		[i for i in folder.iterdir() if 'forward.trimmed.paired' in i.name][0]
		manual_result = True
	except IndexError:
		manual_result = False

	if default_result or manual_result:
		return 'trimmomatic'

	# Test if the folder contains the output from shovill
	# Need to test before 'spades' since both contain a `contigs.fa` file.
	# TODO: make sure this can identify incomplete shovill folders as well.
	expected_shovill = folder / "contigs.fa"
	expected_shovill_spades = folder / "spades.fasta"
	if expected_shovill.exists() and expected_shovill_spades.exists():
		return 'shovill'

	# Test if the folder contains the output from spades.
	expected_spades = folder / "contigs.fa"
	if expected_spades.exists():
		return 'spades'

	# Test if it is a breseq folder
	expected_index = folder / "output" / "index.html"
	if expected_index.exists():
		return 'breseq'

	# Test if the folder contains the output from prokka.
	# Use the suffixes since the prefixes are user-defined and can be almost anything.
	# The prefixes should all be the same value, so could add that as an additional check later.
	suffixes = [i.suffix for i in folder.iterdir() if i.is_file()]
	# Don't need to test for all the files, just the most important ones.
	expected_suffixes = ['.fna', '.ffn', '.gff', '.gbk']
	if all(i in suffixes for i in expected_suffixes):
		return 'prokka'

	if any(i.name.startswith('GCA_') for i in folder.iterdir()):
		return 'genbank'
	if any(i.name.startswith('GCF_') for i in folder.iterdir()):
		return 'refseq'

	if not silent:
		message = f"Cannot determine what the type of folder for '{folder}'"
		raise ValueError(message)
	return None  # Not needed, but clarifies the return value.


def get_file_by_type(folder: Path, suffix: str) -> Optional[Path]:
	""" Extracts a file by the suffix. If no files with the suffix are found or more than one file is found returns `None`"""
	if not suffix.startswith('.'):
		suffix = '.' + suffix
	candidates = [i for i in folder.iterdir() if i.suffix == suffix]
	if len(candidates) == 1:
		filename = candidates[0]
	else:
		filename = None
	return filename

def copydir(source:Path, destination:Path, touch:bool = False):
	for f in source.iterdir():
		target = destination / f.name
		if touch:
			target.touch()
		else:
			copyfile(f, target)

def copyfile(source:Path, target:Path):
	target.write_bytes(source.read_bytes())