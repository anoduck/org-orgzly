;;; org-orgzly.el --- Export org-agenda to ORGZLY -*- lexical-binding: t -*-

;; Author: Anoduck
;; Maintainer: Anoduck
;; Version: 0.01
;; Package-Requires: (org)
;; Homepage: https://github.com/anoduck
;; Keywords: org orgzly agenda


;; This file is not part of GNU Emacs

;; This program is free software: you can redistribute it and/or modify
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

;; The inspiration and parts of this code was provided by Thomas Parslow and his
;; package org-daypage.

;;; Code:

(require 'org)

;; Define orgzly path
(defvar orgzly-path "~/orgzly")

;; Define orgzly keymap
(defvar orgzly-mode-map
  (let ((map (make-sparse-keymap)))
    map)
  "The key map for orgzly buffers.")

;; Define orgzly today
(defun orgzly-today ()
  "Visit the orgzly file for today."
;;  (org-read-date "" 'totime nil nil (orgzly-date) "")
  (setq date (org-current-time))
  (find-file (expand-file-name (concat orgzly-path (format-time-string "%Y-%m-%d" date) ".org"))))

;; Generate orgzly pages
(defun gen-orgzly ()
  "Generate org pages for orgzly."
  (org-batch-agenda "a"
		    org-agenda-span-to-ndays (quote 7)
		    org-agenda-include-diary nil
		    org-agenda-files (quote (org-agenda-files)))
  )

;; Find Orgzly
(defun find-orgzly (&optional date)
  "Go to the day page for the specified DATE, or todays if none is specified."
  (interactive (list
                (org-read-date "" 'totime nil nil
                               (orgzly-date) "")))
  (setq date (or date (orgzly-date)))
  (find-file (expand-file-name (concat orgzly-path (format-time-string "%Y-%m-%d" date) ".org"))))

;; orgzly previous?
(defun orgzly-p ()
  "Return non-nil if the current buffer is visiting a orgzly."
  (if (orgzly-date)
      t
    nil))


;; -----------------------------------------------------------------------------------------------------------------------
;; The below function needs to be rewritten due to undefined variables being present.
;; -----------------------------------------------------------------------------------------------------------------------
(defun orgzly-date ()
  "Return the date for the orgzly visited by the current buffer or nil if the current buffer isn't visiting a dayage."
  (let ((file (buffer-file-name))
        (root-path (expand-file-name orgzly-path)))
    (if (and file
               (string= root-path (substring file 0 (length root-path)))
               (string-match "\\([0-9]\\{4\\}\\)-\\([0-9]\\{2\\}\\)-\\([0-9]\\{2\\}\\).org$" file))
        (let ((d (i) (string-to-number (match-string i file)))) ;; ---> WTF?
          (encode-time 0 0 0 (d 3) (d 2) (d 1)))
      nil)))
;; ---------------------------------------------------------------------------------------------------------
;; Undefined variables: ( d, i, file)
;; ---------------------------------------------------------------------------------------------------------

(defun maybe-orgzly ()
  "Set up orgzly stuff if the org file being visited is in the orgzly folder."
  (let ((date (orgzly-date)))
    (when date
      ; set up the orgzly key map
      (use-local-map orgzly-mode-map)
      (set-keymap-parent orgzly-mode-map
                         org-mode-map)
      (run-hooks 'orgzly-hook))))

;; Add org-mode-hook
(add-hook 'org-mode-hook 'maybe-orgzly)

(defun orgzly-next ()
  "Next Day for buffer."
  (interactive)
  (find-orgzly
   (days-to-time (+ (time-to-days (orgzly-date))
                       1)))
  (run-hooks 'orgzly-movement-hook))

(defun orgzly-prev ()
  "."
  (interactive)
  (find-orgzly
   (days-to-time (- (time-to-days (orgzly-date))
                       1)))
  (run-hooks 'orgzly-movement-hook))

(defun orgzly-next-week ()
  "."
  (interactive)
  (find-orgzly
   (days-to-time (+ (time-to-days (orgzly-date))
                       7)))
  (run-hooks 'orgzly-movement-hook))

(defun orgzly-prev-week ()
  "."
  (interactive)
  (find-orgzly
   (days-to-time (- (time-to-days (orgzly-date))
                       7)))
  (run-hooks 'orgzly-movement-hook))

(defun todays-orgzly ()
  "Go straight to todays day page without prompting for a date."
  (interactive)
  (find-orgzly)
  (run-hooks 'orgzly-movement-hook))

(defun yesterdays-orgzly ()
  "Go straight to todays day page without prompting for a date."
  (interactive)
  (find-orgzly
   (days-to-time (- (time-to-days (orgzly-date))
                      1)))
  (run-hooks 'orgzly-movement-hook))

(defun orgzly-time-stamp ()
  "Works like (and is basically a thin wrapper round)
org-time-stamp except the default date will be the date of the orgzly."
  (interactive)
  (unless (org-at-timestamp-p)
    (insert "<" (format-time-string "%Y-%m-%d %a" (orgzly-date)) ">")
    (backward-char 1))
  (org-time-stamp nil))

(defun orgzly-new-item ()
  "Switch to the current orgzly and insert a top level heading and a timestamp."
  (interactive)
  (todays-orgzly)
  (goto-char (point-max))
  (if (not (bolp))
      (insert "\n"))
  (insert "* <" (format-time-string "%Y-%m-%d %a" (orgzly-date)) "> "))

;; --------------------------------------------------------------------------------
;; Other parts of Org-Daypage added to init.
;; --------------------------------------------------------------------------------

(defun find-orgzly (&optional date)
  "Go to the day page for the specified date or toady's if none is specified."
  (interactive (list 
                (org-read-date "" 'totime nil nil
                               (current-time) "")))
  (setq date (or date (current-time)))
  (find-file 
       (expand-file-name 
        (concat orgzly-path 
        (format-time-string "%Y-%m-%d" date) ".org")))
  (when (eq 0 (buffer-size))
        ;; Insert an initial for the page
        (insert (concat "* <" 
                        (format-time-string "%Y-%m-%d %a" date) 
                        "> Notes\n\n")
        (beginning-of-buffer)
        (next-line 2))))

(defun todays-orgzly ()
  "Go straight to today's day page without prompting for a date."
  (interactive) 
  (find-orgzly))

(global-set-key "\C-con" 'todays-orgzly)
(global-set-key "\C-coN" 'find-orgzly)
;; --------------------------------------------------------------------------------
;; Org-Orgzly Ends Here
;; --------------------------------------------------------------------------------
(provide 'org-orgzly)
;;; org-orgzly.el ends here
