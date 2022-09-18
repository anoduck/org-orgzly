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

(defun orgzly-gen-week ()
  "Create 'org-agenda' for today and write."
  (org-batch-agenda "a"
		    org-agenda-span (quote week)
		    org-agenda-include-diary nil
		    org-agenda-files
		    )
  (org-agenda-write (concat orgzly-path orgzly-today ".org"))
    )


(provide 'org-orgzly-test)
;;; org-orgzly-test.el ends here
