<pre>
  ___  ___  ___ _____ __   __
 / _ \| _ \/ __|_  / |\ \ / /
| (_) |   / (_ |/ /| |_\ V /
 \___/|_|_\\___/___|____|_|
</pre>

## Org-Orgzly

<s>An EMACS package to generate files for orgzly from org agenda files.</s>

Very very early stages of development.

### Who needs ELisp anyway?

*I probably do*

So, programming in elisp is not as fun as I thought it would be. Then came the entire
question of "What exactly are we attempting to accomplish here?". This put aside elisp
for a spell, because it was easier to write something in a language I was familiar with
 while hashing out the details of this project, than both hashing and learning elisp all
 at the same time.

### Current Status

As of right now the script does one thing, and that is search through a solitary file,
acquire either the deadline or the scheduled date of a task, compare that date to today's date,
if it is dated after today, it adds those tasks to a seperate file in the directory you
plan on syncing to orgzly.

### TODO List

- [ ] Do not add tasks after one week from today. (use timeparse)
- [ ] Create a configuration file. (Done before)
- [ ] Allow it to handle multiple files. (should be no problem)
- [ ] Change node range to equate to count of nodes in file or files.

### License

<pre>
 !-- Copyright (C) 2022  anoduck
 !--
 !-- Permission is hereby granted, free of charge, to any person obtaining a copy
 !-- of this software and associated documentation files (the "Software"), to deal
 !-- in the Software without restriction, including without limitation the rights
 !-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 !-- copies of the Software, and to permit persons to whom the Software is
 !-- furnished to do so, subject to the following conditions:
 !-- The above copyright notice and this permission notice shall be included in
 !-- all copies or substantial portions of the Software.
 !--
 !-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 !-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 !-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 !-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 !-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 !-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 !-- THE SOFTWARE.
</pre>
