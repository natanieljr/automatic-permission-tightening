import os
from Levenshtein import distance
from auxiliar import read_file


def compare(layout_folder):
    print("Processing %s" % layout_folder)
    files = []
    for layout_file in os.listdir(layout_folder):
        if '.xml' in layout_file:
            path = os.path.join(layout_folder, layout_file)
            files.append(path)

    res = []
    for i in xrange(len(files)):
        for j in xrange(i + 1, len(files)):
            f1 = read_file(files[i])
            f2 = read_file(files[j])
            d = distance(str(f1), str(f2))
            print("%d \t\t %s \t %s" % (d, os.path.basename(files[i]), os.path.basename(files[j])))
            res.append([d, os.path.basename(files[i]), os.path.basename(files[j])])

    equiv_file_name = os.path.join(layout_folder, 'distance.txt')
    equiv_file = open(equiv_file_name, 'w')

    for l in res:
        equiv_file.write("%d\t%s\t%s" % (l[0], l[1], l[2]))

    equiv_file.close()

    pass


def process(base_dir):
    for f in os.listdir(base_dir):
        if f == 'com.trivago_v1_9_2':
            layout_folder = os.path.join(base_dir, f, 'raw_data', 'unique')
            if os.path.isdir(layout_folder):
                compare(layout_folder)

b_dir = 'data/exploration/first-run/'
process(b_dir)