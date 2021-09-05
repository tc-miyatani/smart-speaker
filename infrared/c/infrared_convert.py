#coding: UTF-8

import os, sys, re

class WriteClass():
    def __init__(self, fp):
        self.fp = fp

    def write(self, text):
        self.fp.write(text)
        sys.stdout.write(text)

def convert(file):
    f = open(file)
    fp = open(file + '.dat', 'w')
    w = WriteClass(fp)

    i = 0
    while 1:
        line = f.readline()
        if not line: break
        if "Using" in line or "Warning" in line: continue
        if re.search('space\s\d{5,}', line): continue

        s = int(line.split(' ')[1].strip())
        if i % 6 == 0:#6信号毎に改行
            w.write("\n% 17d" % s)#各行先頭
        else:
            w.write("% 7d" % s)#各行先頭以外

        i += 1
    print

    f.close
    fp.close()

def main():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if re.search('\.(py|dat|conf)$', file): continue
            print file
            convert(file)
        break
    os.system('@pause')

if __name__ == '__main__':
        main()

