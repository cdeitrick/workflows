from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from loguru import logger

from pipelines import utilities


@dataclass
class SampleReads:
	name: str
	forward: Path
	reverse: Path
	folder: Optional[Path] = None

	def exists(self):
		return self.forward.exists() and self.reverse.exists()

	@classmethod
	def from_folder(cls, folder: Path, sample_id: Optional[str] = None) -> 'SampleReads':
		forward, reverse = utilities.get_reads_from_folder(folder)
		if not sample_id:
			# This will raise a FileNotFoundError if the reads cannot be found. Don't try to ignore the error.
			sample_id = utilities.get_name_from_reads(forward)

		return SampleReads(name = sample_id, forward = forward, reverse = reverse)

	def reads(self) -> List[Path]:
		return [self.forward, self.reverse]


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


def verify_samples(samples: List[SampleReads]) -> bool:
	"""
		Verifies that all samples exist.
	Parameters
	----------
	samples: List[SampleReads]
		A list of samples to test.
	"""
	all_exist = True
	for sample in samples:
		if not sample.exists():
			logger.warning(f"The read files for sample {sample.name} do not exist.")
			logger.warning(f"\tForward Read: {sample.forward}")
			logger.warning(f"\tReverse Read: {sample.reverse}")
			all_exist = False
	return all_exist
