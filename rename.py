import os

file = 0

path = os.getcwd()
path = path + '/corpus1/1/'
for files in os.listdir(path):
    if '.txt' not in files:
        src = path+files
        dst = path+str(file)
        os.rename(src, dst)
        file +=1

path = os.getcwd()
path = path + '/corpus1/2/'
for files in os.listdir(path):
    if '.txt' not in files:
        src = path + files
        dst = path + str(file)
        os.rename(src, dst)
        file +=1

path = os.getcwd()
path = path + '/corpus1/3/'
for files in os.listdir(path):
    if '.txt' not in files:
        src = path + files
        dst = path + str(file)
        os.rename(src, dst)
        file +=1

