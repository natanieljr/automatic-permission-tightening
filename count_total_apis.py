import os

path = 'data/exploration/first-run'

for app in os.listdir(path):
    if os.path.isdir(os.path.join(path, app)):
        p = os.path.join(path, app, 'summary.txt')
        f = open(p)
        data = f.readlines()
        f.close()

        for l in data:
            if l.startswith('Unique API calls count observed in the run: '):
                print('%s\t%s' % (app, l.replace('Unique API calls count observed in the run: ', '').strip()))
                break