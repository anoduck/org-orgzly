<pre>
                                  _
 ___ _ _ __ _ ___ ___ _ _ __ _ __| |_  _
/ _ \ '_/ _` |___/ _ \ '_/ _` |_ / | || |
\___/_| \__, |   \___/_| \__, /__|_|\_, |
        |___/            |___/      |__/

</pre>

## Org-Orgzly

_A python application to parse and generate org files for syncing with orgzly._

### What the hell is this?

A python script to make time management using orgzly more practical.

#### What it does

This script takes a list of org files, extracts org entries from them, parses the dates and TODO keywords, tests
if open entries fall within the designated time range of days, and then writes those entries
to the inbox file in the orgzly directory.

#### Methodological Assumptions

There are several assumptions made concerning time management and an individuals use of orgzly:

* He/She does not desire to sync all of there org-agenda-files with orgzly.
* They have found mobile management of org entries to be not as convenient as when using their local setup.
* The individual does not desire to have tasks that are purely for syncing with orgzly.
* Also the individual does not desire to have duplicate tasks in their org files on their local computer.
* It would be more convenient to only have a few org entries on orgzly, rather than their entire set. 

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
* configobj
* validate

### The Configuration File

The configuration file should be located in your `XDG_CONFIG_HOME` directory, if not, one should be created for you with the default
values.

__DO NOT TOUCH THE SPEC FILE, `configspec.ini`!__

### How to use it:

```bash
usage: main.py [-h] [-i Org Files] [-o Orgzly File] [-n Org Inbox File] [-p Orgzly Inbox File] [-d] [-s]

Filters org entries and prepares them for sync with orgzly

optional arguments:
  -h, --help            show this help message and exit
  -i Org Files, --org_files Org Files
                        an org file to parse for entries
  -o Orgzly File, --orgzly_files Orgzly File
                        orgzly file to push entries to
  -n Org Inbox File, --org_inbox Org Inbox File
                        The org file you desire to push entries from orgzly to
  -p Orgzly Inbox File, --orgzly_inbox Orgzly Inbox File
                        The orgzly file you desire to push entries from orgzly to
  -d, --days            Number of days you want parsed for orgzly
  -s, --sync            Enables pulling entries from orgzly to org

This would be something meaningful
```

Navigate to the repository directory and run `python main.py [OPTIONS]` and it should process the desired file
and generate the other desired file in it's designated location. 

The default options are:

| Option       | Default             |
|--------------|---------------------|
| org_files    | "~/org/TODO.org"    |
| orgzly_files | "~/orgzly/todo.org" |
| org_inbox    | "~/org/inbox.org"   |
| orgzly_inbox | "~/orgzly/inbox.org |
| days         | 7                   |
| sync         | false               |


#### Troubleshooting

If you receive an error while running the script stating `file not found`, then create an empty file for your desired orgzly file. 
This can simply be done with `touch /path/to/orgzly/todo.org`.


### TODO List

- [x] Do not add tasks after one week from today.
- [x] Create a configuration file. (Done before)
- [ ] Complete updating this dame readme file.
- [ ] Allow other "todo keywords" other than "TODO", such as "NEXT", "OPEN", and "HOLD".
- [ ] Allow inserting custom org file headings.
- [x] Allow it to handle multiple files. (should be no problem)
- [ ] Create an org-capture to add items to the orgzly file.
- [x] Change node range to equate to count of nodes in file or files.

### Thanks

This application is dedicated to [karlicoss](https://github.com/karlicoss) to whom without it
would have never been possible. All the credit goes to his [orgparse](https://github.com/karlicoss/orgparse)
library that allows parsing org files in python.  
And, of course, as usual, an additional thanks goes out to the org-mode development team, who have diligently 
maintained one of the most brilliant organisational systems I have seen.  
