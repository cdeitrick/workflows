from loguru import logger
from pathlib import Path


import sys
directory = Path(__file__).parent.parent.absolute()
sys.path.append(str(directory))

from pipelines import sampleio
from pipelines.processes import read_assembly

def main():

	logger.info("Running Assembly pipeline...")
	lipuma_folder = Path.home() / "projects" / "lipuma" #/ "2019-07-24-update"
	source_folder = lipuma_folder / "genomes" / "reads" / "trimmedMajor/"
	parent_folder = lipuma_folder / "2019-07-24-update"

	folders = list(source_folder.iterdir())
	samples = [sampleio.SampleReads.from_trimmomatic(i, i.name) for i in folders]

	read_assembly.read_assembly(samples, parent_folder)

if __name__ == "__main__":
	main()