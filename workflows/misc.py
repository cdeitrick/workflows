a = """
1 AU1143 S17,
2 AU1746 S21,
3 SC1402 S61,
4 AU18616 S76,
5 AU18616 S3,
6 AU6319 S44,
7 AU1142 S16,
8 AU25990 S5,
9 AU25991 S6,
10 AU1064 S14,
11 AU1141 S15,
12 AU12824 S66,
13 AU15410 S72,
14 AU2428 S25,
15 SC1360 S57,
16 AU2427 S24,
17 AU3828 S35,
18 AU6667 S45,
19 AU2986 S27,
20 AU10643 S59,
21 AU3060 S28,
22 AU6668 S46,
23 AU8675 S53,
24 AU20364 S79,
25 AU6015 S43,
26 PC676 S47,
27 PC674 S45,
28 PC669 S43,
29 PC675 S46,
30 PC678 S49,
31 AU4359 S39,
32 AU1056 S12,
33 AU1057 S13,
34 AU1051 S10,
35 AU1055 S11,
36 SC1371 S58,
37 SC1407 S62,
38 SC1419 S63,
39 SC1420 S64,
40 SC1421 S65,
41 AU3739 S31,
42 AU3416 S30,
43 SC1435 S66,
44 AU0465 S7,
45 AU3415 S29,
46 SC1128 S50,
47 SC1129 S51,
48 SC1145 S52,
49 SC1209 S53,
50 SC1210 S54,
51 SC1211 S55,
52 SC1339 S56,
53 SC1392 S59,
54 SC1400 S60,
55 PC677 S48,
56 PC673 S44,
57 AU0074 S1,
58 AU4276 S38,
59 AU0201 S4,
60 AU20865 S80,
61 AU21755 S83,
62 AU23407 S84,
63 AU23516 S1,
64 AU15033 S70,
65 AU0075 S2,
66 AU0106 S3,
67 AU31639 S11,
68 AU35919 S17,
69 AU20866 S81,
70 AU14286 S69,
71 AU36973 S21,
72 AU33869 S14,
73 AU36284 S19,
74 AU36474 S20,
75 AU37865 S23,
76 AU0300 S5,
77 Reference,
78 PC668 S42,
79 AU24509 S2,
80 HI3284 S30,
81 HI3289 S35,
82 AU30919 S10
"""

if __name__ == "__main__":
	from pathlib import Path
	sequence_folder =  Path.home() / "projects" / "lipuma" / "sequences"
	output_filename = sequence_folder / "samples.tsv"
	whitelist = [i for i in a.split('\n') if i]
	whitelist = [i.split(' ')[1] for i in whitelist]

	candidates = list(i.absolute() for i in sequence_folder.glob("**/*"))

	filenames = dict()
	for candidate in candidates:
		name = candidate.stem
		name = name.partition('_')[0]
		if name in whitelist:
			if name in filenames:
				filenames[name].append(candidate)
			else:
				filenames[name] = [candidate]

	t = list()
	for sample_name, reads in filenames.items():
		forward = [i for i in reads if '_R1_' in str(i)][0]
		reverse = [i for i in reads if '_R2_' in str(i)][0]

		row = {
			'sampleName': sample_name,
			'forwardRead': forward,
			'reverseRead': reverse
		}
		t.append(row)
	import pandas
	df = pandas.DataFrame(t)
	print(output_filename)
	df.to_csv(str(output_filename), sep = "\t", index = False)