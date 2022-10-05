<pre>
                                  _
 ___ _ _ __ _ ___ ___ _ _ __ _ __| |_  _
/ _ \ '_/ _` |___/ _ \ '_/ _` |_ / | || |
\___/_| \__, |   \___/_| \__, /__|_|\_, |
        |___/            |___/      |__/

</pre>

## Org-Orgzly

_A python application to parse and generate org files for orgzly, in a practical manner._

### What the hell is this?

A python script to select org entries within a specified number of days and add those entries to your inbox file within your orgzly
directory.  

#### What it does

This script takes a specified list of org files, extracts org entries, parses dates and TODOs to match parameters, provides allowances
for leap years, and then writes those entries to the inbox file of the orgzly directory. It also can be used to then later parse
entries from within your orgzly directory and writes them to your org inbox file.  

#### Methodological Assumptions

There are several assumptions made concerning time management, and an individuals use of orgzly:  

* The user does not desire to sync all org agenda files with orgzly.
* Mobile management of many org entries is difficult.
* Duplicate org entries are not cool.
* Only having a few entries covering the immediate future is all that is needed.

### What is required:

Admittedly, there are many limitations to the application, so don't go all willy nilly on it. In order for the program to discover and
use your nodes, you will need to use the todo keyword "TODO". Other "todo keywords" are not currently supported, but in the works.
Entries are also required to have either an active timestamp, both deadline and scheduled work. It is through these timestamps that
tasks are selected for adding to your orgzly file.  

#### Required python libraries are:

* orgparse
* configobj
* validate

### The Configuration File

The configuration file should be located in your `XDG_CONFIG_HOME` directory in the `org-orgzly` folder. If one cannot be found, the
script should create one for you using the default values.  

An example of the configuration file with default values should look like:  

```ini
# org-orgzly configuration file
org_files = ~/org/todo.org, ~/org/inbox.org
orgzly_files = ~/orgzly/todo.org,
org_inbox = ~/org/inbox.org
orgzly_inbox = ~/orgzly/inbox.org
days = 7
sync = False
```

### How to use it:

__Command line arguments are being phased out, and use of the configuration file is much more preferable.__

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

Navigate to the repository directory and run `python main.py`. This should create a configuration file for you with the default values,
or read a pre-existing configuration file. It should then perform the process with the specified parameters in the config file.

The default options are:

| Option       | Default             |
|--------------|---------------------|
| org_files    | "~/org/todo.org"    |
| orgzly_files | "~/orgzly/todo.org" |
| org_inbox    | "~/org/inbox.org"   |
| orgzly_inbox | "~/orgzly/inbox.org |
| days         | 7                   |
| sync         | false               |

#### Troubleshooting

If you receive an error while running the script referring to a `file not found`, then please take the time to ensure all org files do
exist and are located in their designated folders according to the configuration file.  

If any file needs to be created, this can simply be done with a `touch /path/to/missing/file.org`.  

### TODO List

- [x] Do not add tasks after one week from today.
- [x] Create a configuration file. (Done before)
- [x] Complete updating this dame readme file.
- [ ] Allow other "todo keywords" other than "TODO", such as "NEXT", "OPEN", and "HOLD".
- [x] Allow it to handle multiple files. (should be no problem)
- [ ] Create an org-capture to add items to the orgzly file.
- [x] Change node range to equate to count of nodes in file or files.

### Thanks

This application is dedicated to [karlicoss](https://github.com/karlicoss) to whom without it would have never been possible. All the
credit goes to his [orgparse](https://github.com/karlicoss/orgparse) library that allows parsing org files in python.  

And, of course, as usual, an additional thanks goes out to the org-mode development team, who have diligently maintained one of the
most brilliant organisational systems I have seen.  
