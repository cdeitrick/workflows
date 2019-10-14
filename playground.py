import re
from pathlib import Path

if __name__ == "__main__":
	filenames = [
		Path("mySampleFiltered_1P.fq.gz"),
		Path("mySampleFiltered_1U.fq.gz"),
		Path("mySampleFiltered_2P.fq.gz"),
		Path("mySampleFiltered_2U.fq.gz")
	]

	for i in filenames:
		print(i.match("*[12][PU][.]*"))
