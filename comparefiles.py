# encoding: utf-8
import os
import sys
import hashlib

def main(fileextension: str, directory=""):     
    """Main program."""
    # Parse directory.
    parseddirectory = parsedirectory(directory)
    if parseddirectory != "":
        print("Searching {}...".format(parseddirectory))

        # Get list of all files.
        files, searchscope = getallfiles(fileextension, parseddirectory, recursive=True)
        if searchscope == "subfolders":
            print("Searched {} {} file(s) in all subdirectories".format(len(files), fileextension))
        else:
            print("Searched {} {} file(s) in current directory".format(len(files), fileextension))

        # Compare all files and get list of identical files.
        matchedfiles = findidentical(files)
        print("Found {} matches".format(len(matchedfiles)))

        # Display list of identical files.
        displayidenticalfiles(matchedfiles, fullfilenames=False, groupfiles=True)
    else:
        # Couldn't parse directory.
        print("Directory not found:", directory)

def parsedirectory(directory: str) -> str:
    """Check for valid directory name. If empty, use current directory. If directory does not exist, return empty string."""
    if directory == "":
        return(os.getcwd())
    else:
        # Check if valid directory.
        if os.path.exists(directory):
            return(os.path.join(directory))
    return("")

def getallfiles(fileextension: str, directory: str, recursive=True) -> (list, str):
    """Get all matching files in current directory and subdirectories and their MD5 hash."""
    l = []
    if recursive:
        # Search files in all subdirectories.
        searchscope = "subfolders"
        for rootdir, subdirs, files in os.walk(directory):
            for file in files:
                if fileextension in file:
                    filename = os.path.join(rootdir, file)
                    l.append({"filename": file, "md5": md5(filename), "absolutefilename": filename, "relativefilename": filename.replace(directory, "")})
    else:
        # Search files only in current directory.
        searchscope = "folder"
        for file in os.listdir(directory):          
            if fileextension in file:
                filename = os.path.join(directory, file)
                l.append({"filename": file, "md5": md5(filename), "absolutefilename": filename, "relativefilename": filename})
    return(l, searchscope)

def md5(filename: str) -> str:
    """Return MD5 hash from file."""
    md5hash = hashlib.md5()
    try:
        with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                        md5hash.update(chunk)
    except FileNotFoundError:
        print("Couldn't find {}".format(filename))
    return md5hash.hexdigest()

def findidentical(files: list) -> int:
    """Get a list of all files where their MD5 hashes match. This is slow (n*n), but easy to do..."""
    l = []
    for currentfile in files:
        for comparefile in files:
            if (currentfile["md5"] == comparefile["md5"]) and (currentfile["absolutefilename"] != comparefile["absolutefilename"]):
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
            # Print with two space separation for compatability with md5sum.
            if fullfilenames:
                print(file["md5"], "", file["relativefilename"])
            else:
                print(file["md5"], "", file["filename"])
            last_hash = file["md5"]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            # File extension and folder.
            main(sys.argv[1], sys.argv[2])
        else:
            # File extension.
            main(sys.argv[1])
    else:
        print("Please supply a parameter for a file extension to search for (or . to search all files).")
        print("Usage:   python {} [extension] [folder]".format(sys.argv[0]))
        print("Example: python {} .txt".format(sys.argv[0]))
        print("Example: python {} . C:\sites".format(sys.argv[0]))
