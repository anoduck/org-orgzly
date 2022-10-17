<pre>
  ___  ___  ___    ___  ___  ___ _____ __   __
 / _ \| _ \/ __|  / _ \| _ \/ __|_  / |\ \ / /
| (_) |   / (_ | | (_) |   / (_ |/ /| |_\ V /
 \___/|_|_\\___|  \___/|_|_\\___/___|____|_|
</pre>

## Org-Orgzly

_A python application to parse and generate org files for orgzly, in a practical manner making
managing your org schedule easier._

### About

#### What it does

This script takes a specified list of org files, extracts org entries, parses dates and TODOs to match parameters, provides allowances
for leap years, and then writes those entries to the inbox file of the orgzly directory. It also can be used to then later parse
entries from within your orgzly directory and writes them to your org inbox file.

#### Features

* Processes org nodes for only a particularly defined amount of days, and add them to your orgzly inbox.
* Allows for retrieving created org nodes inside your orgzly inbox to your org inbox.
* Compensates for leap years.
* Uploads orgzly files to a defined folder in your dropbox account.
* Downloads orgzly files to a defined local folder on your local machine.

#### Methodological Assumptions

There are several assumptions made concerning time management, and an individuals use of orgzly:

* The user does not desire to sync all org agenda files with orgzly.
* Mobile management of many org entries is difficult.
* Duplicate org entries are not cool.
* Only having a few entries covering the immediate future is all that is needed.

### What is required:

Admittedly, there are many limitations to the application, so don't go all willy nilly on it. In order for the program to discover and
use your nodes, you will need to use a todo keyword, and either a deadline or a scheduled date. Traversal of multileveled org entries
should be capable, due to the script processing all entries that possess the previously required properties.

### Configuration:

#### Required python libraries are:

* orgparse
* configobj

#### The `ini` file:

The configuration file, `config.ini` will be automatically generated for you in your `XDG_CONFIG_HOME` directory under the `org-orgzly`
folder, with the default values already filled out for you. If you plan on using this script in conjunction with
the Dropbox service, then you will need to change the values of `app_key` and `app_secret` respectively with
the values corresponding to the app your created in the dropbox
[App Console](https://www.dropbox.com/developers/apps?_tk=pilot_lp&_ad=topbar4&_camp=myapps "Dropbox app").
More information can be found out concerning the dropbox api below.

The default configuration varables are as follows:

| Option       | Default             |
|--------------|---------------------|
| app_key      | "Change This"       |
| app_secret   | "Change This"       |
| dropbox_folder | "/orgzly"         |
| orgzly_folder | "~/orgzly"         |
| org_files    | "~/org/todo.org"    |
| orgzly_files | "~/orgzly/todo.org" |
| org_inbox    | "~/org/inbox.org"   |
| orgzly_inbox | "~/orgzly/inbox.org |
| days         | 7                   |
| todos | ["TODO", "LATERS", "HOLD", "OPEN"] |
| dones | ["DONE", "CLOSED", "CANCELED"] |

For redundancy, the configuration file spec is as follows:

```ini
app_key = string(default='Replace with your dropbox app key')
app_secret = string(default='Replace with your dropbox app secret')
dropbox_folder = string(default='orgzly')
orgzly_folder = string(default='~/orgzly')
org_files = list(default=list('~/org/todo.org', '~/org/inbox.org'))
orgzly_files = list(default=list('~/orgzly/todo.org',))
org_inbox = string(default='~/org/inbox.org')
orgzly_inbox = string(default='~/orgzly/inbox.org')
days = integer(default=7)
todos = list(default=list('TODO', 'LATERS', 'HOLD', 'OPEN'))
dones = list(default=list('DONE', 'CLOSED', 'CANCELED'))
```

### Usage:

__Command line arguments will change in distant releases to better reflect subcommands, rather than flagged commands.__

Navigate to the repository directory and run `python org-orgzly.py` or create a simple script in your `$PATH` that points to the repository
and run it whereever.

| Command Flags | What they do       |
|--------------|---------------------|
| --push    | Parses org files and copies entries matching parameters to orgzly inbox  |
| --pull    | Copies newly created entries in orgzly inbox to your og inbox |
| --put     | Uploads orgzly to Dropbox |
| --get     | Downloads orgzly files from dropbox |

The intention of the above "flagged commands" is for them to be run individually to ensure completion and that
they are executed in the proper order.

__Please note!__ In order to avoid reception of a file conflict error, "overwrite mode" has been enabled for
the dropbox api until a means to handle these conflicts can be worked out.

### Troubleshooting

If you receive an error while running the script referring to a `file not found`, then please take the time to ensure all org files do
exist and are located in their designated folders according to the configuration file. If any file needs to be created, this can simply be
done with a `touch /path/to/missing/file.org`.

If you encounter any issues or bugs, please feel free to submit and issue for us to assisst. If there are also
any desired feature requests, you may also fill out an issue labeling it as a "Feature Request".

### Dropbox App Creation and Credentials

Creating a new dropbox app is not that difficult as long as you have a pre-existing Dropbox account. All you
need to do is browse over to the [Dropbox developers site](https://developers.dropbox.com/ "Dropbox Developers") and click the `App Console`
button located in the top right corner of the site. From there you will see a list of all apps you have
created, if you have created any previously. Under the drop down menu of your Dropbox Name, and to the right
of the title "My Apps", you will see a bright blue button labeled "Create app". Click it, and then create your
app by filling out the required parts.

1. You will only be allowed to choose the "Scoped access" API, so select it.
2. Next it will ask what type of access you need. Select, "App Folder" for better security.
3. Lastly on this page, it will ask for you to provide a name. Whatever name you choose, it must not contain the phrase "dropbox". Once done, click the "Create app" button.
4. Before you write down your App key and secret, there is some extra configuration required.
5. Select the "Permissions" tab, and make sure the following boxes are checked to enable the correct
   permissions.

   - [ ] files.metadata.write
   - [ ] files.metadata.read
   - [ ] files.content.write
   - [ ] files.content.read

   Without these selected, the app will not be able to upload and download Dropbox files.

6. Once complete, click on the "submit" button located in the middle-bottom of your screen.
7. You know can return to the "Settings" page and write down your app key and app secret for use in the
   script.

### Thanks

This application is dedicated to [karlicoss](https://github.com/karlicoss) to whom without it would have never been possible. All the
credit goes to his [orgparse](https://github.com/karlicoss/orgparse) library that allows parsing org files in python.

And, of course, as usual, an additional thanks goes out to the org-mode development team, who have diligently maintained one of the
most brilliant organisational systems I have seen.
