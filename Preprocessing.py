import os


def preProcessing(folder):
    path = os.getcwd()
    data_set = "\corpus1/" + folder
    path = path + data_set


allow = True
while allow:
    directory = input("Select a directory out of 1, 2 or 3\n")
    if directory is "1" or directory is "2" or directory is "3":
        allow = False
        preProcessing(directory)

