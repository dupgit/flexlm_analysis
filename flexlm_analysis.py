#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  flexlm_analysis.py : Script to analyse flexlm log files
#
#  (C) Copyright 2013i - 2017 Olivier Delhomme
#  e-mail : olivier.delhomme@free.fr
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

import argparse
import re
import gzip


class Options:
    """
    A class to manage command line options
    """

    files = []           # file list that we will read looking for entries
    out = 'None'         # Character string to choose which output we want:
                         # 'stat' or 'gnuplot'
    image = 'image.png'  # Image name to be included in the gnuplot script
    description = {}
    options = None

    def __init__(self):
        """
        Inits the class
        """
        self.files = []
        self.out = 'None'
        self.image = 'image.png'
        self.description = {}
        self.options = None

        self._get_command_line_arguments()

    # End of init() function


    def _get_command_line_arguments(self):
        """
        Defines and gets all the arguments for the command line using
        argparse module. This function is called in the __init__ function
        of this class.
        """
        str_version = 'flexlm_analysis'

        parser = argparse.ArgumentParser(description='Script to analyse flexlm log files.', version=str_version)

        parser.add_argument('-i', '--image', action='store', dest='image', help='Tells the image name the gnuplot script may generate', default='image.png')
        parser.add_argument('-g', '--gnuplot', action='store_true', dest='gnuplot', help='Outputs a gnuplot script that can be executed later to generate an image about the usage', default=False)
        parser.add_argument('-s', '--stats', action='store_true', dest='stats', help='Outputs some stats about the use of the modules as stated in the log file', default=False)
        parser.add_argument('files', metavar='Files', type=str, nargs='+', help='Log files to be parsed')

        self.options = parser.parse_args()

        if self.options.gnuplot:
            self.out = 'gnuplot'

        if self.options.stats:
            self.out = 'stat'

        self.image = self.options.image
        self.files = self.options.files

    # End of get_command_line_arguments() function
# End of Options class


def read_files(files):
    """Matches lines in the files and returns the number of days in use and a
    list of the following tuple : (date, time, state, module, user, machine).
    """

# 8:21:20 (lmgrd) FLEXnet Licensing (v10.8.0 build 18869) started on MACHINE (IBM PC) (7/30/2012)

    result_list = []
    nb_days = 0
    date_matched = False

    # Reading each file here, one after the other.
    for a_file in files:

        # Openning the files with gzip if they end with .gz, in normal mode
        # if not. Do we need bz2 ? May be we should do this with a magic number
        if '.gz' in a_file:
            inode = gzip.open(a_file, 'r')
        else:
            inode = open(a_file, 'r')

        date = '??/??/????'  # Some unknown date
        old_date = ''

        for line in inode:
            # Looking for some patterns in the file

            if date_matched is False:
                # Look for the line below to guess the starting date (here : 2012/7/30)
                # 8:21:20 (lmgrd) FLEXnet Licensing (v10.8.0 build 18869) started on MACHINE (IBM PC) (7/30/2012)
                res = re.match(r'\ ?\d+:\d+:\d+ .+ \((\d+)/(\d+)/(\d+)\)', line)
                if res:
                    # Formating like this : year/month/day
                    date = '%s/%s/%s' % (res.group(3), res.group(1), res.group(2))
                    date_matched = True

            # 11:50:22 (orglab) OUT: "Origin7" user@MACHINE-NAME
            res = re.match(r'\ ?(\d+:\d+:\d+) .+ (\w+): "(.+)" (\w+)@(.+)', line)
            if res:
                # I put the results in variables for clarity
                time = res.group(1)
                state = res.group(2)
                module = res.group(3)
                user = res.group(4)
                machine = res.group(5)
                result_list.append((date, time, state, module, user, machine))
            else:
                # Trying this patern instead :
                # 20:52:29 (lmgrd) TIMESTAMP 1/23/2012
                res = re.match(r'\ ?\d+:\d+:\d+ .+ TIMESTAMP (\d+)\/(\d+)\/(\d+)', line)
                if res:
                    # Formating like this : year/month/day
                    date = '%s/%s/%s' % (res.group(3), res.group(1), res.group(2))
                    if date != old_date:
                        nb_days = nb_days + 1
                        old_date = date

        inode.close()

    # Returning the total number of days seen in the log file and the
    # list containing all tuples
    return (nb_days, result_list)

# End of read_files function


def get_stats_from_module(stats, module_list, module):
    """Returns the tuple corresponding to the module
    from stats dictionary and takes care to create one
    if its a new module.
    """

    if module not in module_list:
        module_list.append(module)
        stats[module] = (0, 999999999999, '', -1, 0, 0)

    return stats[module]

# End of get_stats_from_module() function


def do_some_stats(result_list):
    """Here we do some stats and fill a dictionnary of stats that will
    contain all stats per module ie one tuple containing the following :
    (max_users, min_users, max_day, nb_users, total_use, nb_days).

    Returns a dictionnary of statistics and a list of module that has stats.
    """

    old_date = 'XXXXXXX'  # A value that does not exists
    # nb_days = 0           # Total number of days of use

    module_list = []
    stats = dict()  # Tuple dictionnary : (max_users, min_users, max_day, nb_users, total_use, nb_days)

    for data in result_list:
        (date, time, state, module, user, machine) = data

        # Retrieving usage values for a specific module
        (max_users, min_users, max_day, nb_users, total_use, nb_days) = get_stats_from_module(stats, module_list, module)

        # Calculating statistics
        if date != old_date:

            if nb_users < 0:
                nb_users = 1

            nb_days = nb_days + 1
            old_date = date

        if state.lower() == 'out':
            nb_users = nb_users + 1
            total_use = total_use + 1

        elif state.lower() == 'in':
            nb_users = nb_users - 1

        if nb_users > 0 and nb_users > max_users:
            max_users = nb_users
            max_day = date

        if nb_users > 0 and nb_users < min_users:
            min_users = nb_users

        # Saving the new values
        stats[module] = (max_users, min_users, max_day, nb_users, total_use, nb_days)

    return (stats, module_list)

# End of do_some_stats function


def print_stats(nb_days, stats, name_list):
    """Prints the stats module per module to the screen.
    """

    for name in name_list:
        (max_users, min_users, max_day, nb_users, total_use, nb_use_days) = stats[name]

        print('Module %s :' % name)
        print(' Number of users per day :')
        print('  max : %d (%s)' % (max_users, max_day))

        if (nb_use_days > 0):
            print('  avg : %d' % (total_use/nb_use_days))

        print('  min : %d' % min_users)

        print(' Total number of use : %d' % total_use)
        print(' Number of days used : %d / %d' % (nb_use_days, nb_days))
        print('')  # Fancier things

# End of print_stats function


def output_stats(nb_days, result_list):
    """Does some stats on the result list and prints them on the screen.
    """

    (stats, name_list) = do_some_stats(result_list)
    print_stats(nb_days, stats, name_list)

# End of output_stats


def do_gnuplot_stats(result_list):
    """Here we do some gnuplot style stats in order to draw an image of the
    evolution of the use of the modules.

    event_list contains the date, time and number of used licenses in reverse
    chronological order.
    """

    module_list = []
    stats = dict()

    for data in result_list:
        (date, time, state, module, user, machine) = data

        if module not in module_list:
            module_list.append(module)
            stats[module] = []   # Creating an empty list of tuples for this new module.

        event_list = stats[module]

        if event_list == []:
            if state.lower() == 'out':
                use = 1
            elif state.lower == 'in':
                use = 0

            event_list.insert(0, (date, time, use))  # Prepending to the list

        else:
            (some_date, some_time, use) = event_list[0]  # retrieving the last 'use' value to update it

            if state.lower() == 'out':
                use = use + 1
            elif state.lower() == 'in':
                use = use - 1

            event_list.insert(0, (date, time, use))  # Prepending to the list

        stats[module] = event_list

    return (stats, module_list)

# End of do_some_stats function


def print_gnuplot(image_name, nb_days, stats, module_list):
    """Writing the data files and the gnuplot script.
    """

    # Generating the gnuplot script
    gnuplot_file = open('gnuplot.script', 'w')

    gnuplot_file.write('set key right\n')
    gnuplot_file.write('set grid\n')
    gnuplot_file.write('set title "FlexLm"\n')
    gnuplot_file.write('set xdata time\n')
    gnuplot_file.write('set timefmt "%Y/%m/%d %H:%M:%S"\n')
    gnuplot_file.write('set format x "%Y/%m/%d %H:%M:%S"\n')
    gnuplot_file.write('set xlabel "Date"\n')
    gnuplot_file.write('set ylabel "Nombre d\'executions"\n')
    gnuplot_file.write('set output "%s"\n' % image_name)
    gnuplot_file.write('set style line 1 lw 1\n')
    gnuplot_file.write('set terminal png size %d,1024\n' % (24*nb_days))
    gnuplot_file.write('plot ')

    first_line = True

    # Generating data files. Their names are based upon the module name being analysed
    for m in module_list:
        dat_filename = '%s.dat' % m
        dat_file = open(dat_filename, 'w')

        if first_line:
            gnuplot_file.write('"%s" using 1:3 title "%s" with lines' % (dat_filename, m))
            first_line = False
        else:
            gnuplot_file.write(', \\\n"%s" using 1:3 title "%s" with lines' % (dat_filename, m))

        event_list = stats[m]
        event_list.reverse()  # We have to reverse the list as we prepended elements

        for event in event_list:
            (date, time, use) = event
            dat_file.write('%s %s %d\n' % (date, time, use))

        dat_file.close()

# End of print_gnuplot() function


def output_gnuplot(image_name, nb_days, result_list):
    """Does some stats and outputs them into some data files and a gnuplot script
    that one might run later.
    """

    (stats, module_list) = do_gnuplot_stats(result_list)
    print_gnuplot(image_name, nb_days, stats, module_list)

# End of output_gnuplot() function


def main():
    """Here we choose what to do upon the command line's options.
    """

    # Parsing options
    my_opts = Options()

    (nb_days, result_list) = read_files(my_opts.files)

    if len(result_list) > 1:

        if my_opts.out == 'stat':
            output_stats(nb_days, result_list)

        # We do not want to generate an image if the number of day usage is less than one !
        elif my_opts.out == 'gnuplot' and nb_days > 0:
            output_gnuplot(my_opts.image, nb_days, result_list)

if __name__ == "__main__":
    main()
