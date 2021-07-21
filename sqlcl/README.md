README 
------

 Name: SQL Developer SQLcl
 Desc: Oracle SQL Developer Command Line (SQLcl) is a free command line 
       interface for Oracle Database. It allows you to interactively or 
       batch execute SQL and PL/SQL. SQLcl provides in-line editing, statement
       completion, and command recall for a feature-rich experience, all while
       also supporting your previously written SQL*Plus scripts.
 Version: 21.2.0
 Build: 21.2.0.174.2245

Release Notes 


Release 21.2
============

From Release 21.2, the console has been upgraded which has meant changes to several subsystems in SQLcl, namely
  * Multiline Editing
  * history
  * keymaps - Support for VI and EMACS (set editor, show keymap)
And we have built upon that to include several new features
  * Highlighting - set highlight on
  * Statusbar - set statusbar on
  * Completers - File, tns, net and argument
  * Extensions - API has been published for creating SQLcl extension. View them with "show extensions"

Some other things of note:
Memory settings:
  We've put the max memory settings to 2gb now to accommodate very large buffers 

Copy/Paste functionality:
  Paste will act differently on Mac vs Windows/Linux.
  On Windows/Linux, a paste will process all statements individually as they are read in.
  On Mac, a paste will process statements altogether at the end of the paste.
  All results are the same in each case. The printed output will differ if echo is on.

Scrolling on Windows Terminal:
  In some situations when using Windows Terminal, the terminal window scroll bar becomes deactivated when using status bar.
  This issue has not been observed when using either Command Prompt or PowerShell.

Status Bar and resize:
  Occasionally when using status bar and following a terminal window resize, unexpected characters have been seen in the terminal window.
  If this occurs, then control-L may be used to clear and redraw the terminal window.


Release 20.2
============

Ansiconsole as default SQLFormat
--------------------------------
From SQLcl 20.2, AnsiConsole Format is on by default.  This means that certain 
features will not work as expect until the format is set to default.

These include the SQL\*Plus features
  * HEADING
  * TTITLE
  * BREAK
  * COMPUTE

SQL> set sqlformat default. 

If you have extensive use of SQL\*Plus style reports, you need to unset
sqlformat via login.sql or add it to your reports
