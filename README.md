<style>
.logo {
      text-align: center;
      width: 300px;
   }
</style>
<div class="log">
![org-orgzly](./org-orgzly_logo.png)
</div>

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

This script takes a specified list of org files, extracts org entries, filters out entries that do not meet specified TODO and Date
parameters, provides allowances for days in a month and leap years, and then writes those entries to the designated orgzly inbox. It
then uploads designated orgzly files to Dropbox. Then it allows the user to download those files from Dropbox, and add newly added or
changed entries found within the orgzly inbox to the org inbox for categorization and re-filing.

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

### What is required / Configuration:

Admittedly, there are many limitations to the application, so don't go all willy nilly on it. In order for the program to discover and
use your nodes, you will need to use a todo keyword, and either a deadline or a scheduled date. Traversal of multileveled org entries
should be capable, due to the script processing all entries that possess the previously required properties.

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

All configuration values are **REQUIRED**, and although they do provide the user to customize the script, there are some systematic
implementations that must be accommodated in facilitation of your org-task management system. Most notably is the implementation of an
"Inbox" file to place new and unorganized tasks into. The other is the separation of org and orgzly files in order to ensure the org
file tree remains clean and protected from any unfortunate circumstances. This separation also allows one to maintain their org files
in a version control management system without any conflicts with use of Dropbox.

*Point of information* - The Dropbox API does implement it's own form of version control management in order to prevent file conflicts
and loss of information within it's internal network. It is this internal version control management system that is often the cause of
problems when newly created file content is overwritten and/or lost. This is the benefit of using a direct upload approach to managing
files on the Dropbox platform. Updates are instantaneous and take priority.

The default configuration varables are as follows:

| Option         | Default                                     | Definitions                                                      |
|----------------|---------------------------------------------|------------------------------------------------------------------|
| app_key        | "Change This"                               | Dropbox API App Key                                              |
| app_secret     | "Change This"                               | Dropbox API APP Secret                                           |
| dropbox_folder | "/orgzly"                                   | Name of folder for orgzly in dropbox                             |
| org_files      | ["~/org/todo.org", "~/org/inbox.org"]       | Comma seperated list of org files to process entries/nodes from. |
| orgzly_files   | ["~/orgzly/todo.org", "~/orgzly/inbox.org"] | Comma seperated orgzly file list to use with this entire system  |
| org_inbox      | "~/org/inbox.org"                           | Name of org mode inbox file to push new or changed entries to    |
| orgzly_inbox   | "~/orgzly/inbox.org                         | Name of orgzly inbox to add new or changed entries to            |
| days           | 7                                           | Number of days to draw entries / nodes for                       |
| todos          | ["TODO", "LATERS", "HOLD", "OPEN"]          | Org "TODO" keywords defining an uncomplete task                  |
| dones          | ["DONE", "CLOSED", "CANCELED"]              | Org "DONE" keywords defining a complete task                     |

For redundancy, the configuration file spec is as follows:

```ini
app_key = string(default='Replace with your dropbox app key')
app_secret = string(default='Replace with your dropbox app secret')
dropbox_folder = string(default='orgzly')
org_files = list(default=list('~/org/todo.org', '~/org/inbox.org'))
orgzly_files = list(default=list('~/orgzly/todo.org',))
org_inbox = string(default='~/org/inbox.org')
orgzly_inbox = string(default='~/orgzly/inbox.org')
days = integer(default=7)
todos = list(default=list('TODO', 'LATERS', 'HOLD', 'OPEN'))
dones = list(default=list('DONE', 'CLOSED', 'CANCELED'))
```

### Usage:

__Please note!__ In order to avoid reception of a file conflict error using the Dropbox API, "overwrite mode" has been enabled for the
dropbox api until a means to handle these conflicts can be worked out.

**PLEASE MAKE BACKUPS OF YOUR FILES IN CASE OF THE UNFORTUNATE**

Navigate to the repository directory and run `python org-orgzly.py`, or create an alias in your script `rc` file, create a simple
script in your `$PATH` that points to the repository and run it where ever, or even add it to cron. All should work since things are
kept together in a single file. An example of creating an alias for ZSH or Bash is below:

```sh

alias org-orgzly="/path/to/python /path/to/org-orgzly/org-orgzly.py"

```

Below are the four commands available for org-orgzly. See __usage__ for instructions on what order to execute them.

| Command Flags | What they do                                                            |
|---------------|-------------------------------------------------------------------------|
| --push        | Parses org files and copies entries matching parameters to orgzly inbox |
| --pull        | Copies newly created entries in orgzly inbox to your og inbox           |
| --put         | Uploads orgzly to Dropbox                                               |
| --get         | Downloads orgzly files from dropbox                                     |

The intention of the above "flagged commands" is for them to run individually, and for the most part this is required, as not doing so
could be very messy and lead to data loss. The intended command flow is as follows.

#### Recommended workflow

* First, move entries to orgzly, and use __push__ and __put__
* Then, at a later point in time, retrieve entries from orgzly, and use __get__ and __pull__

##### Sequence of execution
1. `--push`: Push to orgzly
2. `--put`: Put in Dropbox
3. `--get`: Get from Dropbox
4. `--pull`: Pull from orgzly

![Cycle of Operation](https://www.plantuml.com/plantuml/svg/3SR13O8X30RGLNG0_-_kDgKW44jBAWtHwUNmadVloXAvXCkjhJK_Ju0jbrIyNkOLf9Q3tpX_73_vmcaZEIat3EgAbzY-PWpv0m00)

### Troubleshooting

If you receive an error while running the script referring to a `file not found`, then please take the time to ensure all org files do
exist and are located in their designated folders according to the configuration file. If any file needs to be created, this can simply be
done with a `touch /path/to/missing/file.org`.

If you encounter any issues or bugs, please feel free to submit and issue for us to assisst. If there are also
any desired feature requests, you may also fill out an issue labeling it as a "Feature Request".

### Dropbox App Creation and Credentials

Creating a new dropbox app is not that difficult as long as you have a pre-existing Dropbox account. All you
need to do is [login to Dropbox](https://www.dropbox.com/login "Dropbox Login") browse over to the [Dropbox developers
site](https://developers.dropbox.com/ "Dropbox Developers") and click the `App Console` button located in the top right corner of the
site. From there you will see a list of all apps you have created, if you have created any previously. Under the drop down menu of your
Dropbox Name, and to the right of the title "My Apps", you will see a bright blue button labeled "Create app". Click it, and then
create your app by filling out the required parts.

1. You will only be allowed to choose the "Scoped access" API, so select it.
2. Next it will ask what type of access you need. Select, "App Folder" for better security.
3. Lastly on this page, it will ask for you to provide a name. Whatever name you choose, it must not contain the phrase "dropbox". Once done, click the "Create app" button.
4. Before you write down your App key and secret, there is some extra configuration required.
5. Select the "Permissions" tab, and make sure the following boxes are checked to enable the correct
   permissions.

   - [x] files.metadata.write
   - [x] files.metadata.read
   - [x] files.content.write
   - [x] files.content.read

   Without these selected, the app will not be able to upload and download Dropbox files.

6. Once complete, click on the "submit" button located in the middle-bottom of your screen.
7. You know can return to the "Settings" page and write down your app key and app secret for use in the
   script.

### Future Features

- [ ] Creation of missing org files if any
- [ ] Single file duplicate removal
- [ ] Node list duplicate removal
- [ ] Implement a better CLI

### Thanks

This application is dedicated to [karlicoss](https://github.com/karlicoss) to whom without it would have never been possible. All the
credit goes to his [orgparse](https://github.com/karlicoss/orgparse) library that allows parsing org files in python.

And, of course, as usual, an additional thanks goes out to the [org-mode development team](https://orgmode.org "Org Mode"), who have diligently maintained the
most brilliant organizational systems ever.
