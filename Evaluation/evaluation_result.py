# coding:utf-8

# 统计人工评分结果，标准差，使用t检验验证显著性

import math
from scipy import stats
import pandas as pd

method_name = ['Lead-sen     ', 'Coverage-sen ', 'Centroid-sen ', 'TextRank-sen ', 'Centroid-tile', 'TextRank-tile',
               'INS          ']

score_table = []

f = open('./result.txt', 'r')
while True:
    name = f.readline().strip()
    if len(name) < 2:
        break
    cur_table = []
    for i in range(0, 7):
        scores = f.readline().strip().split()
        scores = [float(s) for s in scores]
        cur_table.append(scores)
    score_table.append(cur_table)
f.close()

# 计算平均值
result_table = [[0.0 for i in range(0, 5)] for j in range(0, 7)]
for table in score_table:
    for i in range(0, 7):
        for j in range(0, 5):
            result_table[i][j] += table[i][j]
for i in range(0, 7):
    for j in range(0, 5):
        result_table[i][j] /= len(score_table)
        result_table[i][j] = round(result_table[i][j], 3)
print 'Ave\n'
for i in range(0, 7):
    print method_name[i], result_table[i]

# 计算标准差
dev_table = [[0.0 for i in range(0, 5)] for j in range(0, 7)]
for table in score_table:
    for i in range(0, 7):
        for j in range(0, 5):
            dev_table[i][j] += pow(table[i][j] - result_table[i][j], 2)
for i in range(0, 7):
    for j in range(0, 5):
        dev_table[i][j] = math.sqrt(dev_table[i][j] / len(score_table))
        dev_table[i][j] = round(dev_table[i][j], 3)
print '\nDev\n'
for i in range(0, 7):
    print method_name[i], dev_table[i]

# 进行t检验
print '\nT-test\n'
p_table = [[0.0 for i in range(0, 5)] for j in range(0, 6)]  # 记录对应的p-value
for i in range(0, 6):
    for j in range(0, 5):
        print i, j
        # 先将对应的数据写入tmp.csv文件中
        f_csv = open('tmp.csv', 'w')
        f_csv.write('a,b\n')
        for table in score_table:
            f_csv.write(str(table[i][j]) + ',' + str(table[6][j]) + '\n')
        f_csv.close()
        paired = pd.read_csv('tmp.csv')
        print stats.ttest_rel(paired["a"], paired["b"])


