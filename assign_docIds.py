import os

file = 0
path = os.getcwd()
newfile1 = path + "\doc_id1.txt"
file1 = open(newfile1, "w+", encoding='latin-1', errors='ignore')
newfile2 = path + "\doc_id2.txt"
file2 = open(newfile2, "w+", encoding='latin-1', errors='ignore')
newfile3 = path + "\doc_id3.txt"
file3 = open(newfile3, "w+", encoding='latin-1', errors='ignore')

path = path + '/corpus1/1/'
for files in os.listdir(path):
    if '.txt' not in files:
        file1.write(files+":"+str(file))
        file1.write("\n")
        file +=1

path = os.getcwd()
path = path + '/corpus1/2/'
for files in os.listdir(path):
    if '.txt' not in files:
        file2.write(files+":"+str(file))
        file2.write("\n")
        file +=1

path = os.getcwd()
path = path + '/corpus1/3/'
for files in os.listdir(path):
    if '.txt' not in files:
        file3.write(files+":"+str(file))
        file3.write("\n")
        file += 1

