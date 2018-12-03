#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import string
import hashlib
from fuzzywuzzy import fuzz
from itertools import combinations

__version__ = "0.1.0"
__author__ = "Peter M. Dahlgren"
__copyright__ = "(C) Peter M. Dahlgren"

class CompareFileBase():
    """Base class for file comparisons."""

    def __init__(self, file_extension: str, directory=""):
        """Constructor."""
        self.file_extension = self.parse_file_extension(file_extension)
        self.directory = self.parse_directory(directory)
        self.num_files = 0
        self.num_searched_files = 0
        self.files = []
        if self.directory != "":
            self.directory_exists = True
        else:
            self.directory_exists = False
    
    @property
    def before_message(self):
        """Get message before running comparison."""
        return "Searching for files {} in {}".format(self.file_extension, self.directory)

    @property
    def during_message(self):
        """Get message during running comparison."""
        return "Identified {} files".format(self.num_searched_files)

    @property
    def after_message(self):
        """Get message after running comparison."""
        return "Found {} files".format(self.num_files)

    def parse_directory(self, directory: str) -> str:
        """Check for valid directory name. If empty, use current directory. If directory does not exist, return empty string."""
        if directory == "":
            return os.getcwd()
        else:
            if os.path.exists(directory):
                return os.path.join(directory)
        return "" 

    def parse_file_extension(self, file_extension: str) -> str:
        """Check for valid file extensions, and correct explicit file extensions (e.g., *.txt --> .txt)."""
        if file_extension.find("*.") > -1:
            file_extension = file_extension.replace("*.", ".")
        return file_extension.lower()

    def get_all_files(self) -> list:
        """Get all files (matching file extension) in current directory and subdirectories."""
        l = []
        for rootdir, subdirs, files in os.walk(self.directory):
            for filename in files:
                if self.is_file_extension_same(filename, self.file_extension):
                    l.append(os.path.join(rootdir, filename))
        return l

    def is_file_extension_same(self, filename, file_extension) -> bool:
        if file_extension in [".", "*", "*.*", ".*"]:
            return True
        _, ext = os.path.splitext(filename.lower())
        if ext.lower() == file_extension.lower():
            return True
        return False

    def get_relative_filename(self, filename: str) -> str:
        """Get relative filename from absolute filename."""
        return filename.replace(self.directory, "")


class CompareIdentical(CompareFileBase):
    """Compare files if they are identical."""

    def __init__(self, file_extension: str, directory=""):
        """Constructor."""
        super().__init__(file_extension, directory)
        self.num_matches = 0

    @property
    def before_message(self):
        """Get message before running comparison."""
        return "Searching for identical {} files in {}...".format(self.file_extension, self.directory)

    @property
    def after_message(self):
        """Get message after running comparison."""
        if self.num_matches == 0:
            return "Found 0 files"
        elif self.num_searched_files == 1:
            return ("Found only 1 file, need at least 2 for comparisons")
        else:
            return "Found {} matches across {} files".format(self.num_matches, self.num_files)

    def run(self):
        """Main method to run comparison."""
        print(self.before_message, flush=True)
        self.searched_files = self.get_all_files()
        self.num_searched_files = len(self.searched_files)
        if self.num_searched_files > 0:
            print(self.during_message, flush=True)
            self.files = self.compare_all_files(self.searched_files)
            self.display_files(self.files)
            self.num_matches = self._count_unique_hashes(self.files)
        self.num_files = len(self.files)
        print()
        print(self.after_message)

    def compare_all_files(self, files: list) -> list:
        """Get all identical files, with their MD5 hashes."""
        l = []
        for file in files:
            l.append({"filename": file, "md5": self._md5(file)})
        return self._get_identical_files(l)

    def _md5(self, filename: str) -> str:
        """Return MD5 hash from file."""
        md5hash = hashlib.md5()
        try:
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5hash.update(chunk)
        except FileNotFoundError:
            print("Couldn't read {}".format(filename))
        return md5hash.hexdigest()

    def _get_identical_files(self, files: list) -> list:
        """Get a list of all files where their MD5 hashes match. This is slow (n*n), but easy to do..."""
        l = []
        for currentfile in files:
            for comparefile in files:
                if (currentfile["md5"] == comparefile["md5"]) and (currentfile["filename"] != comparefile["filename"]):
                    l.append(currentfile)
        return(self._remove_duplicate_dicts(l))

    def _remove_duplicate_dicts(self, lst: list) -> list:
        """Remove duplicate dictionaries from a list."""
        return([dict(t) for t in {tuple(d.items()) for d in lst}])

    def _count_unique_hashes(self, lst: list, key="md5") -> int:
        """Count the number of unique hashes in list with dictionaries."""
        return(len(set([(lambda k: k[key])(k) for k in lst])))

    def display_files(self, files: list):
        """Display files that are identical. Group files together."""
        if len(files) > 0:
            last_hash = ""
            for file in sorted(files, key=lambda k: k["md5"]):
                if last_hash != file["md5"]:
                    print()
                print("{}  {}".format(file["md5"], self.get_relative_filename(file["filename"])))
                last_hash = file["md5"]


class CompareSimilarity(CompareFileBase):
    """Compare text files if they are similar."""

    def __init__(self, file_extension: str, directory="", sort=False, algorithm="ratio"):
        """Constructor."""
        super().__init__(file_extension, directory)
        self.sort = sort
        self.num_matches = 0
        self.min_similarity = 0
        self.max_similarity = 0
        self.avg_similarity = 0
        if algorithm in ["ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio"]:
            self.algorithm = algorithm
        else:
            raise ValueError("Invalid algorithm '{}'. Specify 'ratio', 'partial_ratio', 'token_sort_ratio' or 'token_set_ratio'.".format(algorithm))
   
    @property
    def before_message(self):
        """Get message before running comparison."""
        return "Searching for similar {} files in {}...".format(self.file_extension, self.directory)

    @property
    def after_message(self):
        """Get message after running comparison."""
        if self.num_searched_files == 0 or self.num_files == 0:
            return "Found 0 files"
        elif self.num_searched_files == 1:
            return ("Found only 1 file, need at least 2 for comparisons")
        elif self.num_searched_files == 2:
            return "Compared {} files".format(self.num_searched_files)
        else:
            return "Compared {} files ({} combinations), similarity range: {}-{}% (average {}%)".format(self.num_searched_files,
                                                                                        self.num_combinations,
                                                                                        self.min_similarity,
                                                                                        self.max_similarity,
                                                                                        round(self.avg_similarity))

    def run(self):
        """Main method to run comparison."""
        print(self.before_message, flush=True)
        self.searched_files = self.get_all_files()
        self.num_searched_files = len(self.searched_files)
        if self.num_searched_files > 0:
            print(self.during_message, flush=True)
            if self.sort:
                # Sort first, then print.
                for file in sorted(self.compare_all_files(self.searched_files), key=lambda k: k["similarity"], reverse=True):
                    self.files.append(file)
                print()
                self.display_files(self.files)
            else:
                # Print as soon as any comparison is done.
                print()
                for file in self.compare_all_files(self.searched_files):
                    self.files.append(file)
                    self.print_fileset(file)
            self.num_files = len(self.files)
        self._set_similarity_summary_stats(self.files)
        print()
        print(self.after_message)

    def _set_similarity_summary_stats(self, files, key="similarity"):
        """Calculate summary statistics: min similarity, max similarity, and average similarity."""
        if len(files) > 0:
            self.min_similarity = min([(lambda f: f[key])(f) for f in files])
            self.max_similarity = max([(lambda f: f[key])(f) for f in files])
            self.avg_similarity = sum([(lambda f: f[key])(f) for f in files]) / len(files)

    def compare_all_files(self, files: list) -> dict:
        """Compare similarities bewtween all combinations of files."""
        self.num_combinations = sum(1 for i in combinations(files, 2))
        l = []
        for file_set in combinations(files, 2):
            similarity = self._get_similarity_ratio(file_set[0], file_set[1])
            if similarity > 0:
                yield {"filename1" : file_set[0], 
                       "filename2" : file_set[1], 
                       "similarity": similarity}
        
    def _get_similarity_ratio(self, filename1: str, filename2: str) -> int:
        """Compare similarity between two files and return similarity score (0-100)."""
        content1, content2 = self._read_file_contents(filename1), self._read_file_contents(filename2)
        if content1 == "" and content2 == "":
            return -1
        if self.algorithm == "ratio":
            return fuzz.ratio(content1, content2)             # Simple ratio. Fast.
        elif self.algorithm == "partial_ratio":
            return fuzz.partial_ratio(content1, content2)     # Partial ratio. Slow.
        elif self.algorithm == "token_sort_ratio":
            return fuzz.token_sort_ratio(content1, content2)  # Token sort ratio. Fast.
        elif self.algorithm == "token_set_ratio":
            return fuzz.token_set_ratio(content1, content2)   # Token set ratio. Fast.
        raise ValueError()

    def _read_file_contents(self, filename: str) -> str:
        """Read file contents and return it as a string."""
        try:
            with open(filename, encoding="utf8") as f:
                c = f.readlines()
            return "".join(c)
        except IOError as e:
            print(e)
            return ""
        except UnicodeDecodeError as e:
            # Don't print decode errors - we assume these files are binary.
            return ""

    def display_files(self, files: list):
        """Print similar set of files on screen."""
        for file in files:
            self.print_fileset(file)

    def print_fileset(self, file):
        """Print pair of files and their similarity (in percent)."""
        print("{} {}  {}".format((str(file["similarity"]) + "%").ljust(5), 
                                self.get_relative_filename(file["filename1"]).ljust(35),
                                self.get_relative_filename(file["filename2"])))


def main(args):
    """Main program."""
    if args.identical:
        # Search for identical files.
        comp = CompareIdentical(file_extension=args.file_extension, directory=args.directory)
        if not comp.directory_exists:
            print("Directory not found:", args.directory)
            return
        comp.run()
    if args.similar:
        # Search for similar text files.
        try:
            comp = CompareSimilarity(file_extension=args.file_extension, directory=args.directory, sort=args.sort, algorithm=args.algorithm)
        except ValueError as e:
            print(e)
            return
        if not comp.directory_exists:
            print("Directory not found:", args.directory)
            return
        comp.run()

if __name__ == "__main__": 
    # Define arguments, and parse them.
    parser = argparse.ArgumentParser(description="Compare all files in a directory for either identical files or similar files.", epilog="If you check for identical files, only the files with identical MD5 hashes will be printed to screen. If you check for file similarity (--similar), percent similarity for each file pair will be printed to screen (note: similarity is only available for text files).")
    parser.add_argument("--sort", dest="sort", action="store_true", required=False, help="sort files by similarity (descending)")
    parser.add_argument("--ext", metavar="extension", type=str, dest="file_extension", default=".txt", required=False, help="limit comparison to this file extensions (default: .txt)")
    parser.add_argument("--dir", metavar="directory", dest="directory", type=str, default="", required=False, help="directory to search recursively (default: current directory)")
    parser.add_argument("--algorithm", metavar="name", dest="algorithm", type=str, default="ratio", required=False, help="name of similarity algorithm: ratio (default), partial_ratio, token_sort_ratio, token_set_ratio")
    parser.add_argument("--similar", dest="similar", action="store_true", default=False, required=False, help="check if text files are similar")
    parser.add_argument("--identical", dest="identical", action="store_true", default=False, required=False, help="check if files are identical")
    parser.add_argument("--version", dest="version", action="store_true", default=False, required=False, help="show version")
    if len(sys.argv) > 1:
        args = parser.parse_args()
        if args.version:
            print("comparefiles {} {}".format(__version__, __copyright__))
        else:
            main(args)
    else:
        parser.print_help()