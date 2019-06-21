import csv
from pathlib import Path
from typing import List, Optional, Tuple, Union, Iterable
from loguru import logger
from dataclasses import dataclass

def get_name_from_reads(path:Union[str,Path])->str:
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

	def exists(self):
		return self.forward.exists() and self.reverse.exists()
	@classmethod
	def from_folder(cls, folder:Path, sample_id:Optional[str] = None)-> 'SampleReads':
		if not sample_id:
			sample_id = folder.name
		forward, reverse = get_reads_from_folder(folder)

		return SampleReads(name = sample_id, forward = forward, reverse = reverse)
	def reads(self)->Iterable[Path]:
		return [self.forward, self.reverse]


def get_reads_from_folder(folder: Path) -> Tuple[Path, Path]:
	candidates = list(folder.iterdir())
	forward = [i for i in candidates if 'R1' in i.stem][0]
	reverse = [i for i in candidates if 'R2' in i.stem][0]

	return forward, reverse


def get_samples_from_folder(folder:Path)->List[SampleReads]:
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

def validate_samples(samples:List[SampleReads]):
	for sample in samples:
		if not sample.forward.exists() or not sample.reverse.exists():
			logger.error(f"Sample {sample.name} cannot be found.")