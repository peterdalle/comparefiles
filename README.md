# comparefiles

Search for identical files of a given file extension in the current directory and all its subdirectories.

The program calculates a MD5 hash for each file. Files that have an identical hash are then presented on the screen.

Note: the program is very slow when there is a large number of files (due to `n * n * 2` lookups).

## Usage

```bash
$ python comparefiles.py [file extension] [folder]
```

If folder is not set, the current folders is searched.

## Example

The following will search for all `.sav` files in current directory and all subdirectories.

```bash
$ python comparefiles.py .sav
```

Which outputs the following:

```
Searched 29 .sav file(s) in all subdirectories
Found 5 matches

342be2108deefb88c937e79b97f14e96 Copy_1.sav
342be2108deefb88c937e79b97f14e96 Copy_2.sav
342be2108deefb88c937e79b97f14e96 Copy_3.sav

897f385d92d0bd9a73831b37055d90b0 Another_copy_1.sav
897f385d92d0bd9a73831b37055d90b0 Another_copy_2.sav
```

Search for all files (`.`) in the directory `C:\sites` and all its subdirectories:

```bash
$ python comparefiles.py . C:\sites
```
