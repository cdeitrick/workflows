from loguru import logger
from pathlib import Path


import sys
directory = Path(__file__).parent.parent.absolute()
sys.path.append(str(directory))

from pipelines import sampleio
from pipelines.processes import read_assembly

def main():

	logger.info("Running Assembly pipeline...")
	source_folder = Path("/home/cld100/projects/lipuma/genomes/reads/trimmed/")
	parent_folder = source_folder.with_name('trimmed_stringent')

	folders = list(source_folder.iterdir())
	samples = [sampleio.SampleReads.from_trimmomatic(i, i.name) for i in folders]

	read_assembly.read_assembly(samples, parent_folder)

if __name__ == "__main__":
	main()