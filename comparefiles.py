# encoding: utf-8
import os
import sys
import hashlib

def main(fileextension: str):     
        """Main program."""
        # Get list of all files.
        files = getallfiles(fileextension=fileextension)
        print("Searched", len(files), fileextension, "file(s) in all subdirectories")

        # Compare all files and get list of identical files.
        matchedfiles = findidentical(files)
        print("Found", len(matchedfiles), "matches")

        # Display list of identical files.
        displayidenticalfiles(matchedfiles, fullfilenames=False, groupfiles=True)

def getallfiles(fileextension, recursive=True) -> list:
        """Get all matching files (in current directory and subdirectories) and their MD5 hash."""
        l = []
        currentdir = os.getcwd()
        for rootdir, subdirs, files in os.walk(currentdir):
                for file in files:
                        if fileextension in file:
                                filename = os.path.join(rootdir, file)
                                l.append({"file": file, "md5": md5(filename), "fullfilename": filename})
        return(l)

def md5(filename: str) -> str:
        """Return MD5 hash from file."""
        md5hash = hashlib.md5()
        with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                        md5hash.update(chunk)
        return md5hash.hexdigest()

def findidentical(files: list) -> int:
        """Get a list of all files where their MD5 hashes match. This is slow (n*n), but easy to do..."""
        l = []
        for currentfile in files:
                for comparefile in files:
                        if (currentfile["md5"] == comparefile["md5"]) and (currentfile["fullfilename"] != comparefile["fullfilename"]):
                                l.append(currentfile)
        return(removeduplicatedicts(l))

def removeduplicatedicts(lst: list) -> list:
        """Remove duplicate dictionaries from a list."""
        return([dict(t) for t in {tuple(d.items()) for d in lst}])

def displayidenticalfiles(files: list, fullfilenames=True, groupfiles=True):
        """Display files that are identical."""
        if len(files) > 0:
                # Sort files by hash to group them together when printing.
                last_hash = ""
                for file in sorted(files, key=lambda k: k["md5"]):
                        if last_hash != file["md5"] and groupfiles:
                                print()
                        if fullfilenames:
                                print(file["md5"], file["fullfilename"])
                        else:
                                print(file["md5"], file["file"])
                        last_hash = file["md5"]

if __name__ == "__main__":
        if len(sys.argv) > 1:
                main(sys.argv[1])
        else:
                print("Please supply a parameter for a file extension to search for.")
                print("Example: python {0} .txt".format(sys.argv[0]))
