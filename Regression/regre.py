#coding:utf-8

from sklearn import svm



C = 1
clf1 = svm.SVC(C = C,class_weight = {0:1,1:5}, probability=True)
clfwork1 = clf1.fit(X, Y)
# pY = clfwork1.predict_proba(tX)
