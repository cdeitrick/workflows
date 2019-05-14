from pathlib import Path

def run_snippy(assembled_genome, reference, output_folder):
	command = ["snippy",
		"--outdir", output_folder,
		"--ref", reference,
		"--peil", assembled_genome
	]

if __name__ == "__main__":
	reference = ""
	samples = [
		("AU1054", "AU1054.fna", None),
		("HI2424", "HI2424.fna", None),
		("J2315", "J2315.fna", None),
		("PC184", "PC184.fna", None),
		(
			"AU10040",
			"/home/cld100/projects/lipuma/samples/AU10040/AU10040_combined_R1_001.fastq",
			"/home/cld100/projects/lipuma/samples/AU10040/AU10040_combined_R2_001.fastq"
		),
		(
			"AU18616",
			"/home/cld100/projects/lipuma/samples/AU18616/AU18616_combined_R1_001.fastq",
			"/home/cld100/projects/lipuma/samples/AU18616/AU18616_combined_R2_001.fastq"
		)
	]