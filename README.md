<pre>
  ___  ___  ___
 / _ \| _ \/ __|  ___
| (_) |   / (_ | |___|
 \___/|_|_\\___|

  ___  ___  ___ _____ __   __
 / _ \| _ \/ __|_  / |\ \ / /
| (_) |   / (_ |/ /| |_\ V /
 \___/|_|_\\___/___|____|_|
</pre>

## Org-Orgzly

_A python application to parse and generate org files for syncing with orgzly._


### Who needs ELisp anyway?

*I probably do*

So, programming in elisp is not as fun as it should be. Then came the entire
question of "What exactly are we attempting to accomplish here?". This put aside elisp
for a spell, because it was easier to write something in a familiar language 
 while hashing out the details of this project, than both hashing out details and 
 learning elisp all at the same time.  

### Current Status

The script is taking shape, and works. It parses an orgfile extracts entries, tests if those 
entries meet the specified parameters. If they do, then it writes those entries to a file the
user designates in preparation to be synced with orgzly.  

### What is required:

Admittedly, there are many limitations to the application, so don't go all willy nilly on it. In order
for the program to discover and use your nodes, you will need to use a "todo keyword", such as simple "TODO".
Other "todo keywords" have not been tested, so there is a real possibility that you are limited to solely the
"TODO" keyword. Entries are also required to have either a deadline timestamp or a scheduled timestamp. It is
through these timestamps that tasks are selected for adding to your orgzly file.  

A little warning, this script is quite noisy.

Required python libraries are:

* orgparse
* click

### How to use it:

```bash
Usage: main.py [OPTIONS]

Options:
  --org_file TEXT     File to process
  --orgzly_file TEXT  Full path to orgzly file to write to
  --days INTEGER      integer for number of days you want to process for your
                      file.

  --help              Show this message and exit.
```

Navigate to the repository directory and run `python main.py [OPTIONS]` and it should process the desired file
and generate the other desired file in it's designated location. 

The default options are:

| Option      | Default             |
|-------------|---------------------|
| org_file    | "~/org/TODO.org"    |
| orgzly_file | "~/orgzly/todo.org" |
| days        | 7                   |

There was one last significant bit of advice to offer... If only I could remember what exactly it was...

### TODO List

- [x] Do not add tasks after one week from today.
- [ ] Create a configuration file. (Done before)
- [ ] Allow other "todo keywords" other than "TODO", such as "NEXT", "OPEN", and "HOLD".
- [ ] Allow inserting custom org file headings.
- [ ] Allow it to handle multiple files. (should be no problem)
- [ ] Create an org-capture to add items to the orgzly file.
- [x] Change node range to equate to count of nodes in file or files.

### Thanks

This application is dedicated to [karlicoss](https://github.com/karlicoss) to whom without it
would have never been possible. All the credit goes to his [orgparse](https://github.com/karlicoss/orgparse)
library that allows parsing org files in python.  
And, of course, as usual, an additional thanks goes out to the org-mode development team, who have diligently 
maintained one of the most brilliant organisational systems I have seen.  
