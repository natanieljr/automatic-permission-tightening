import os


def mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

    assert os.path.exists(directory)
    assert os.path.isdir(directory)


def read_file(path):
    f = open(path, 'r')
    data = f.readlines()
    f.close()

    return data
