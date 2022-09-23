;;; org-orgzly-test.el --- Test file for development of org-orgzly  -*- lexical-binding: t; -*-

;; Copyright (C) 2022  vassilios

;; Author: vassilios <vassilios@liberator.boobchan.com>
;; Keywords: calendar, local, convenience, extensions, outlines, tools

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <https://www.gnu.org/licenses/>.

;;; Commentary:

;; This is a test file for org-orgzly. So do not load this, and there is
;; really nothing special that is happening here.

;;; Code:
(require 'org)
(require 'parse-time)

;; Define orgzly path
(defvar orgzly-path "~/orgzly/")

;; Define orgzly keymap
(defvar orgzly-mode-map
  (let ((map (make-sparse-keymap)))
    map)
  "The key map for orgzly buffers.")

(defvar orgzly-today
  (let ((today (format-time-string "%Y-%m-%d")))
    today)
  "Define today.")

(defvar orgzly-file-name
  (setq orgzly-file-name (defun orgzly-file-name ()
			   (expand-file-name
			    (re-search-forward
			     (concat "[0-9]\{4\}" "\-" "[0-9]\{2\}" "\-" "[0-9]\{2\}" "\.org")
			     )
			    )
			   )
	)
  )

;; If current buffer is visiting an org file with proper syntax,
;; acquire date from file name. If not, get date from user.
(defvar orgzly-date
  (if (eq (buffer-name) orgzly-file-name)
      (let ((orgzly-date (format-time-string (substring orgzly-file-name 0 10))))
	orgzly-date)
      (let ((orgzly-date(org-read-date(org-calendar-select))))
    orgzly-date)
    )
  )

    ;; "LET ORGZLY-DATE equal date from calendar.")

;; Define orgzly today
(defun orgzly-today ()
  "Visit the orgzly file for today."
  (find-file (expand-file-name (concat orgzly-path (format-time-string "%Y-%m-%d" orgzly-date) ".org"))))

(defun orgzly-gen-week ()
  "Create 'org-agenda' for today and write."
  (org-batch-agenda "a"
		    org-agenda-span-to-ndays (quote 7)
		    org-agenda-include-diary nil
		    org-agenda-files (quote(org-agenda-files))
		    )
  (org-agenda-write (concat orgzly-path orgzly-date ".org"))
    )


(provide 'org-orgzly-test)
;;; org-orgzly-test.el ends here
