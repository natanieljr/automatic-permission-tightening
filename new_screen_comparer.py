import os
from shutil import copyfile
from Levenshtein import distance
from auxiliar import read_file

THRESHOLD = 50


def compare(layout_folder):
    files = []
    for layout_file in os.listdir(layout_folder):
        if '.xml' in layout_file:
            path = os.path.join(layout_folder, layout_file)
            files.append(path)
            #sanitize_file(path)

    res = []
    done = []
    for f in files:
        if f in done:
            continue

        print('Matching screens with file %s' % f)
        f_base = read_file(f)
        res.append([f, []])
        done.append(f)

        for g in files:
            if g not in done:
                f_tmp = read_file(g)
                d = distance(str(f_base), str(f_tmp))
                #print(d)
                if d == 0:
                    res[-1][1].append(g)
                    done.append(g)

    new_dir = os.path.join(layout_folder, 'unique')
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    equiv_file_name = os.path.join(new_dir, 'equiv.txt')
    equiv_file = open(equiv_file_name, 'w')

    for l in res:
        f_name = os.path.basename(l[0])
        new_f = os.path.join(new_dir, f_name)
        copyfile(l[0], new_f)
        tmp = ''
        for a in l[1]:
            tmp += ', ' + a

        if len(tmp) > 0:
            tmp = tmp[1:].strip()

        equiv_file.write('%s\t%s\n' % (l[0], tmp))
        print(l)

    pass


def process(base_dir):
    for f in os.listdir(base_dir):
        if f == 'animaonline.android.wikiexplorer_v1_5_5':
            layout_folder = os.path.join(base_dir, f, 'raw_data')
            if os.path.isdir(layout_folder):
                compare(layout_folder)


def process_with_diff(base_dir):
    for f in os.listdir(base_dir):
        #if f == 'animaonline.android.wikiexplorer_v1_5_5':
        if os.path.isdir(os.path.join(base_dir, f)):
            unique_folder = os.path.join(base_dir, f, 'raw_data', 'unique')
            distance_file = os.path.join(unique_folder, 'distance.txt')
            tmp = read_file(distance_file)
            data = [[int(x.split('\t')[0]), x.split('\t')[1].strip(), x.split('\t')[2].strip()] for x in tmp if len(x) > 0]

            res = []

            for line in data:
                dist = line[0]
                base_val = line[1]
                equiv_val = line[2]

                if base_val not in res:
                    res.append(base_val)

                if dist < THRESHOLD:
                    if equiv_val not in res[res.index(base_val)]:
                        res[res.index(base_val)] += '\t%s' % equiv_val

            print("Before=%d\t After=%d\tFolder=%s" % (len(tmp), len(res), f))

            res = [x.strip().split('\t') for x in res]
            res = sorted(res, key=lambda x: x[0])
            i = 1
            while i < len(res):
                if res[i][0] in res[i - 1]:
                    if len(res[i]) > 1:
                        if res[i][1] not in res[i - 1]:
                            res[i - 1].append(res[i][1])
                    res.remove(res[i])
                else:
                    i += 1

            data = sorted(res, key=lambda x: x[0])
            new_distance_file = os.path.join(unique_folder, 'distance_threshold_50.txt')
            f = open(new_distance_file, 'w')
            for line in res:
                f.write('%s\n' % str(line).replace(',', '\t').replace('[', '').replace(']', '').replace("'", ''))

            f.close()


def merge_equiv_files(base_dir):
    for f in os.listdir(base_dir):
        #if f == 'animaonline.android.wikiexplorer_v1_5_5':
        if os.path.isdir(os.path.join(base_dir, f)):
            raw_data_folder = os.path.join(base_dir, f, 'raw_data')
            unique_folder = os.path.join(raw_data_folder, 'unique')
            distance_file_1 = os.path.join(unique_folder, 'equiv.txt')
            distance_file_2 = os.path.join(unique_folder, 'distance_threshold_50.txt')
            data1 = read_file(distance_file_1)
            data2 = read_file(distance_file_2)
            data2 = [x.split('\t') for x in data2]
            before = len(data1)

            for line in data2:
                base = line[0]
                i = 0
                while i < len(data1):
                    if base in data1[i]:
                        for idx, cell in enumerate(line):
                            if idx > 0:
                                data1[i] = '%s\t%s\n' % (data1[i].strip(), os.path.join(raw_data_folder, cell))

                    i += 1

            i = 0
            data1 = [x.strip().replace('\\ ', '\\').split('\t') for x in data1]
            data1 = sorted(data1, key=lambda x: x[0])
            while i < len(data1):
                if data1[i][0] in data1[i - 1]:
                    if len(data1[i]) > 1:
                        for c in data1[i][1:]:
                            if c not in data1[i - 1]:
                                data1[i - 1].append(c)
                    data1.remove(data1[i])
                else:
                    i += 1

            full_equiv = os.path.join(unique_folder, 'full_equiv.txt')
            f1 = open(full_equiv, 'w')
            for line in data1:
                f1.write('%s\n' % str(line).replace(',', '\t').replace('[', '').replace(']', '').replace("'", ''))

            f1.close()

            print("Before=%d\t After=%d\tFolder=%s" % (before, len(data1), f))


#b_dir = 'data/exploration/first-run/animaonline.android.wikiexplorer_v1_5_5/'
#b_dir = 'data/exploration/first-run/arlind.Shqip_v2_0/'
b_dir = 'data/exploration/first-run/'
#process(b_dir)
#process_with_diff(b_dir)
merge_equiv_files(b_dir)