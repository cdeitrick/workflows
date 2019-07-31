from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

from loguru import logger


def get_name_from_reads(path: Union[str, Path]) -> str:
	# Ex. M64_123_S50_R1_001.fastq
	# Remove the extra stuff added to the filename.
	if isinstance(path, str):
		path = Path(path)
	parts = path.name.split('_')[:-3]
	return "_".join(parts)


@dataclass
class SampleReads:
	name: str
	forward: Path
	reverse: Path
	folder: Optional[Path] = None
	is_trimmed: bool = True

	def exists(self):
		return self.forward.exists() and self.reverse.exists()

	@classmethod
	def from_folder(cls, folder: Path, sample_id: Optional[str] = None) -> 'SampleReads':
		if not sample_id:
			sample_id = folder.name
		forward, reverse = get_reads_from_folder(folder)

		return SampleReads(name = sample_id, forward = forward, reverse = reverse)

	@classmethod
	def from_trimmomatic(cls, folder: Path, sample_id: str) -> Optional['SampleReads']:
		files = list(i for i in folder.iterdir() if i.suffix == ".fastq")
		try:
			forward = [i for i in files if ('forward' in i.name and 'unpaired' not in i.name)][0]
			reverse = [i for i in files if ('reverse' in i.name and 'unpaired' not in i.name)][0]
			return cls(sample_id, forward, reverse, folder, is_trimmed = True)
		except IndexError:
			logger.warning(f"Could not find trimmomatic reads in folder {folder}")
			return None

	def reads(self) -> Iterable[Path]:
		return [self.forward, self.reverse]

def is_forward_read(filename:Path)->bool:
	if 'R1' in filename.stem or ('forward' in filename.stem and 'unpaired' not in filename.stem):
		return True
	return False
def is_reverse_read(filename:Path)->bool:
	if 'R2' in filename.stem or ('reverse' in filename.stem and 'unpaired' not in filename.stem):
		return True
	return False

def get_reads_from_folder(folder: Path) -> Tuple[Path, Path]:
	candidates = list(i for i in folder.iterdir() if i.suffix == '.fastq')
	forward = [i for i in candidates if is_forward_read(i)][0]
	reverse = [i for i in candidates if is_reverse_read(i)][0]

	return forward, reverse


def get_samples_from_folder(folder: Path) -> List[SampleReads]:
	"""Loads all sample folders in a given folder."""
	samples = list()
	for subfolder in folder.iterdir():
		try:
			samples.append(SampleReads.from_folder(subfolder))
		except IndexError:
			# The expected reads do no exist
			logger.warning(f"Cannot find the reads for {subfolder}")
		except NotADirectoryError:
			# There was an extra file in the folder. ignore it.
			pass
	return samples


def validate_samples(samples: List[SampleReads]):
	for sample in samples:
		if not sample.forward.exists() or not sample.reverse.exists():
			logger.error(f"Sample {sample.name} cannot be found.")
