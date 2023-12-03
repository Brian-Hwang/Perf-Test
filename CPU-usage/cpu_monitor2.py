# Usage : python3 top_parse.py <parsing 할 코어 갯수> <코어 #> <코어 #> <코어 #> ...
# e.g. python3 top_parse.py 3 8 9 10
import re
import sys

file_name = sys.argv[1]
f = open (file_name, 'r')
CPU = dict()

idx = 3
for i in range (0, int (sys.argv[2])):
	CPU[int(sys.argv[idx])] = []
	idx += 1

data = f.readlines ()

for l in data:
	l = re.sub (r" +", " ", l)
	d = l.split (" ")
	cpu_num = ''

	for i in range (0, len (d)):
		if "nvmet_tcp_wq" in d[i]:
			end = i
			cpu_num = int(d[i].split ('/')[1].split(':')[0])

		if cpu_num not in CPU.keys():
			continue

		CPU[int(cpu_num)].append (float(d[9]))

for k, v in CPU.items():
	if len(v) != 0:
		print ("CPU #%d : %.4f"% (k, (sum(v) / len(v))))