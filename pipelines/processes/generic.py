from pathlib import Path
from typing import List, Union

from loguru import logger
from pipelines.programs import trimmomatic, shovill
from pipelines.processes import read_assembly
from pipelines import programio, sampleio, utilities


class GenericVariantCalling:
	# Implements a method to run variant calling on any combination of input parameters.
	def __init__(self, project_folder:Path):
		self.project_folder = utilities.checkdir(project_folder)
	def run(self, reference: Union[str, Path], samples: Union[Path, List], output_folder: Path):
		"""
			Attempts to run variant calling by converting the input arguments into the required filetypes.
			This may require the function for invoke other processes, extract the reference from the samples, etc.

		Parameters
		----------
		reference: Union[str,Path]
			This can come in several states:
			- `assembly`: Path (file)
				The reference assembly only exists, so no further manipulation is required.
			- `reads`: Path (folder)
				The raw reads that must be trimmed and assembled in order to have a reference.
			- `trimmed`: Path (folder)
				The trimmed reads that must be assembled in order to have a reference.
			- `sample`: str
				The sample name to use as a reference. Assume that this must be trimmed and assembled.
		samples: Union[Path, sampleio.SampleReads, trimmomatic.TrimmomaticOutput]
			The samples can be provided in several states:
			- `folder`: Path (folder_
				The folder where the sequenced reads are located. These may be trimmed or untrimmed.
			- List[sampleio.SampleReads]
				A list of raw reads for the workflow. These still need to be trimmed.
			- List[trimmomatic.TrimmomaticOutput]
				A list of trimmed reads to include in the workflow.
		samples
		output_folder
		"""

		sample_reads = self.load_samples(samples)  # May need to still trim some.

	@staticmethod
	def load_samples(samples: Union[Path, List]) -> List[sampleio.SampleReads]:
		if isinstance(samples, Path):
			project_samples = get_reads_from_folders(samples)
		else:
			project_samples = samples
		return project_samples


	def process_reference(self, reference: Union[str, Path, sampleio.SampleReads, programio.TrimmomaticOutput]) -> Path:

		# If the reference already points to an assembly, return it without modification.
		if isinstance(reference, Path) and reference.is_file():
			return reference

		# Otherwise, need to convert the input to the path to an assembly.
		# Since the assembly does not yet exist, the input must be a reference to a set of reads.
		# Coerce this reference to either SampleReads or TrimmomaticOutput, which can then be fed through the
		# AssemblyWorkflow.
		# test whether `reference` is a folder pointing to a set of reads.
		if isinstance(reference, Path) and reference.is_dir():
			reference = get_reads_from_folder(reference)

		# `reference` should now be one of the accepts `Reads` objects.
		assembly_workflow = read_assembly.AssemblyWorkflow(self.project_folder)
		reference_assembly = assembly_workflow.assemble_sample(reference, utilities.checkdir(self.project_folder / reference.name))

		return reference_assembly.contigs



def get_reads_from_folder(folder: Path) -> Union[None, sampleio.SampleReads, programio.TrimmomaticOutput]:
	folder_type = utilities.get_folder_type(folder)
	if folder_type == 'reads':
		result = sampleio.SampleReads.from_folder(folder)
	elif folder_type == 'trimmomatic':
		result = programio.TrimmomaticOutput.from_folder(folder)
	else:
		logger.warning(f"Could not load samples from the folder '{folder}'")
		result = None
	return result


def get_reads_from_folders(folder: Path) -> List[Union[sampleio.SampleReads, programio.TrimmomaticOutput]]:
	"""Loads all sample folders in a given folder."""
	samples = list()
	for subfolder in folder.iterdir():
		result = get_reads_from_folder(subfolder)
		if result:
			samples.append(result)
	return samples
