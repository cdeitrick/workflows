import os
import subprocess
from Bio import SeqIO
from pathlib import Path
if __name__ == "__main__":
	filename = Path("/home/cld100/Documents/projects/rosch/prokka_gene_map.txt")
	folder = Path("/home/cld100/Documents/projects/rosch/prokka_gene_search/")
	reference_filename = Path("/home/cld100/Documents/projects/rosch/ref/pneumo.faa")
	reference_filename_base = reference_filename.with_suffix('.ffn')

	reference_amino = SeqIO.to_dict(SeqIO.parse(reference_filename, "fasta"))
	reference_base  = SeqIO.to_dict(SeqIO.parse(reference_filename_base, "fasta"))

	contents = filename.read_text().split('\n')
	for line in contents:
		if not line: continue
		gene_name = line.strip().upper()
		gene_folder = folder / gene_name
		if not gene_folder.exists():
			gene_folder.mkdir()
		sequence_filename = gene_folder / "sequence.fasta"
		sequences = [reference_amino[gene_name], reference_base[gene_name]]
		with sequence_filename.open('w') as output:
			SeqIO.write(sequences, output, "fasta")




