import os
from shutil import copyfile
#from lxml import etree
from Levenshtein import distance
from auxiliar import read_file

"""
def sanitize_node(node):
    if 'text' in node.keys():
        node.set('text', '')
    if len(node) > 0:
        for child in node:
            sanitize_node(child)

def sanitize_file(path):
    f = open(path)
    xml = etree.parse(f)
    f.close()
    root = xml.getroot()

    sanitize_node(root)

    print(etree.tostring(root))
"""

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
        if f == 'com.trivago_v1_9_2':
            layout_folder = os.path.join(base_dir, f, 'raw_data')
            if os.path.isdir(layout_folder):
                compare(layout_folder)

#b_dir = 'data/exploration/first-run/animaonline.android.wikiexplorer_v1_5_5/'
#b_dir = 'data/exploration/first-run/arlind.Shqip_v2_0/'
b_dir = 'data/exploration/first-run/'
process(b_dir)