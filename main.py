#! /usr/bin/env python
# charset: utf-8

import sys, os, shutil, time
from hashlib import sha256
import argparse as ap
from gooey import Gooey, GooeyParser

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def hashFile(file_name):
    ''' https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html '''
    sha256_hash = sha256()
    with open(file_name, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def folderContentDict(source):
    out = {}
    internalCollisions = 0
    toHash = 0
    for e in os.walk(source):
        for fileName in e[2]:
            toHash += 1
    hashed = 0
    for e in os.walk(source):
        for fileName in e[2]:
            dir = os.path.join(*e[0].split(os.path.pathsep))
            fileName = os.path.join(dir, fileName)
            try:
                hash = hashFile(fileName)
            except PermissionError:
                print("Permission denided: {}".format(fileName))
            if hash not in out:
                out[hash] = fileName
            else:
                internalCollisions += 1
            hashed +=1
            print("progress: {}/{}".format(hashed, toHash))
    return out, internalCollisions


def main(source, dest):
    print("Source: {}".format(source))
    print("Dest: {}".format(dest))
    print("Chargement du dictionnaire des signatures du dossier sources.")
    sourceDict, nCollisionsSource = folderContentDict(source)
    print("Chargement du dictionnaire des signatures du dossier de destination.")
    destDict, nCollisionsDest = folderContentDict(dest)
    print("{} elements dans le dictionnaire source. {} collisions".format(len(sourceDict), nCollisionsSource))
    print("{} elements dans le dictionnaire destination. {} collisions".format(len(destDict), nCollisionsDest))
    toMove = 0
    for k in sourceDict:
        if k not in destDict:
            toMove += 1
    moved = 0
    for k in sourceDict:
        if k in destDict:
            print("Skip {} car existe déjà sous le nom : {}".format(sourceDict[k], destDict[k]))
        else:
            target = sourceDict[k].replace(source, dest)
            print("cp {} {}".format(sourceDict[k], target))
            try:
                os.makedirs(os.path.split(target)[0], exist_ok=True)
                shutil.copy(sourceDict[k], target)
                moved += 1 
            except PermissionError:
                print("Permission denied.")
            print("progress: {}/{}".format(moved, toMove))


@Gooey(language="french", progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$", progress_expr="current / total * 100",  hide_progress_msg=True)
def maingui():
    p = GooeyParser(description="Copie avec déduplication")
    p.add_argument("source", widget="DirChooser")
    p.add_argument("dest", widget="DirChooser")
    args = p.parse_args()
    main(args.source, args.dest)


def maincli():
    p = ap.ArgumentParser()
    p.add_argument("--cli", action = "store_true")
    args, unkown = p.parse_known_args()
    if args.cli:
        p.add_argument("source")
        p.add_argument("dest")
        args = p.parse_args()
        main(args.source, args.dest)
    else:
        maingui()

if __name__ == '__main__':
    maincli()