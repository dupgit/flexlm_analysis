flexlm_analysis.py
==================

Script to analyse flexlm log files.

[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dupgit/flexlm_analysis/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/dupgit/flexlm_analysis/?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dupgit/flexlm_analysis/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/dupgit/flexlm_analysis/?branch=master)


Usage
=====

```
NAME
  flexlm_analysis.py

SYNOPSIS
  flexlm_analysis.py [OPTIONS] FILES

DESCRIPTION
  Script to analyse flexlm log files.

OPTIONS

  -h, --help
    This help

  -s, --stat
    Outputs some stats about the use of the modules as stated
    in the log files

  -g, --gnuplot
    Outputs a gnuplot script that can be executed later to
    generate an image about the usage

EXAMPLES
  flexlm_analysis.py origin.log
```
