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

The following will search for all `.py` files in current directory and all subdirectories.

```bash
$ python comparefiles.py .py
```

Which outputs the following:

```
Searching .py in C:\Users\Foo\Code...
Searched 557 file(s) in all subdirectories
Found 3 matches across 9 files

29a6a1e050bd42fe24cd17b138d4b08d  \trackthenews\build\lib\trackthenews\__init__.py
29a6a1e050bd42fe24cd17b138d4b08d  \trackthenews\trackthenews\__init__.py

c52ffcfb32d03e7e0b90138c8d438092  \trackthenews\trackthenews\core.py
c52ffcfb32d03e7e0b90138c8d438092  \trackthenews\build\lib\trackthenews\core.py

d41d8cd98f00b204e9800998ecf8427e  \newsdiffs\website\__init__.py
d41d8cd98f00b204e9800998ecf8427e  \newsdiffs\website\frontend\management\commands\__init__.py
d41d8cd98f00b204e9800998ecf8427e  \newsdiffs\website\frontend\management\__init__.py
d41d8cd98f00b204e9800998ecf8427e  \newsdiffs\website\frontend\__init__.py
d41d8cd98f00b204e9800998ecf8427e  \newsdiffs\website\frontend\migrations\__init__.py
```

Search for all files (`.`) in the directory `C:\sites` and all its subdirectories:

```bash
$ python comparefiles.py . C:\sites
```
