#coding:utf-8
import numpy as np
f = open('result_ui.txt', 'r')
arrays = []
for line in f:
    line = line.strip().split()
    line = [float(t) for t in line]
    ta = np.array(line)
    arrays.append(ta)
f.close()
n = len(arrays)
tol = np.array(7*[0.0])
for ta in arrays:
    tol += ta
#均值
ave = []
for t in tol:
    ave.append(round(t/n, 3))
print ave

#标准差
d = []
for i in range(0, 7):
    s = 0.0
    for ta in arrays:
        s += (ta[i]-ave[i])**2
    s /= n
    s = np.sqrt(s)
    s = round(s, 3)
    d.append(s)
print d

