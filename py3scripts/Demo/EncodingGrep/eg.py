# -*- coding:utf-8 -*-
import os
import fnmatch
import re
from chardet.universaldetector import UniversalDetector
from argparse import ArgumentParser


class EncodingGrep(object):
    def __init__(self):
        self.__options = self.parseCmd()
        self._detector = UniversalDetector()
        self.action()

    def action(self):
        # Todo List:
        # -r -n -H -e --exclude-dir --exclude --include --encoding
        self.grepDir(os.path.abspath(self.__options.glob[0]))

    def grepDir(self, path):
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            if os.path.isdir(fullpath):
                if self.__options.recursive:
                    for subitem in self.__options.exclude_dir:
                        if fnmatch.fnmatch(item, subitem):
                            break
                    else:
                        self.grepDir(fullpath)
            else:
                for subitem in self.__options.exclude:
                    if fnmatch.fnmatch(item, subitem):
                        break
                else:
                    for subitem in self.__options.include:
                        if fnmatch.fnmatch(item, subitem):
                            self.grepFile(fullpath)
                            break

    def grepFile(self, path):
        pat = re.compile(self.__options.regexp[0].encode('utf-8'))
        if self.__options.guess or (self.__options.encoding and len(self.__options.encoding) > 0):
            with open(path, 'rb') as fh:
                data = fh.read()
            if self.__options.guess:
                self._detector.reset()
                self._detector.feed(data)
                self._detector.close()
                data = data.decode(
                    self._detector.result['encoding'] or 'UTF-8', errors='ignore')
            else:
                for testcode in self.__options.encoding:
                    try:
                        data.decode(testcode)
                        data = data.decode(testcode, errors='ignore')
                        break
                    except:
                        pass
                else:
                    data = data.decode('utf-8', errors='ignore')
        else:
            with open(path, 'r', errors='ignore') as fh:
                data = fh.read()

        for idx, line in enumerate(data.splitlines()):
            if pat.search(line.encode('utf-8')):
                print('{path}:{line}:{code}'.format(
                    path=path, line=idx + 1, code=line))

    def parseCmd(self):
        parser = ArgumentParser(add_help=False)
        parser.add_argument('glob', nargs='*', help='File(s)/Dir(s)')
        # Generic Program Information
        parser.add_argument(
            '--help',
            dest='help',
            action='store_true',
            default=False,
            help=
            'Print a usage message briefly summarizing the command-line options and the bug-reporting address, then exit.'
        )
        parser.add_argument(
            '-V',
            '--version',
            dest='version',
            action='store_true',
            default=False,
            help=
            'Print the version number of eg to the standard output stream.')
        # Matching Control
        parser.add_argument(
            '-e',
            '--regexp',
            dest='regexp',
            action='append',
            help='Search patterns')
        parser.add_argument(
            '-f',
            '--file',
            dest='file',
            action='store',
            help=
            'Obtain patterns from file, one per line. The empty file contains zero patterns, and therefore matches nothing.'
        )
        parser.add_argument(
            '-i',
            '--ignore-case',
            dest='ignore_case',
            action='store_true',
            default=False,
            help=
            'Ignore case distinctions in both the patterns and the input files.'
        )
        parser.add_argument(
            '-v',
            '--invert-match',
            dest='invert_match',
            action='store_true',
            default=False,
            help='Invert the sense of matching, to select non-matching lines.')
        parser.add_argument(
            '-w',
            '--word-regexp',
            dest='word_regexp',
            action='store_true',
            default=False,
            help=
            'Select only those lines containing matches that form whole words.')
        parser.add_argument(
            '-x',
            '--line-regexp',
            dest='line_regexp',
            action='store_true',
            default=False,
            help=
            'Select only those matches that exactly match the whole line.')
        # General Output Control
        parser.add_argument(
            '-c',
            '--count',
            dest='count',
            action='store_true',
            default=False,
            help=
            'Suppress normal output; instead print a count of matching lines for each input file. With the ‘-v’, ‘--invert-match’ option, count non-matching lines.'
        )
        parser.add_argument(
            '--color',
            dest='color',
            action='store',
            default='never',
            help=
            'Surround the matched (non-empty) strings, matching lines, context lines, file names, line numbers, byte offsets, and separators (for fields and groups of context lines) with escape sequences to display them in color on the terminal. The colors are defined by the environment variable GREP_COLORS and default to ‘ms=01;31:mc=01;31:sl=:cx=:fn=35:ln=32:bn=32:se=36’ for bold red matched text, magenta file names, green line numbers, green byte offsets, cyan separators, and default terminal colors otherwise. COLOR is ‘never’, ‘always’, or ‘auto’.'
        )
        parser.add_argument(
            '-L',
            '--files-without-match',
            dest='files_without_match',
            action='store_true',
            default=False,
            help=
            'Suppress normal output; instead print the name of each input file from which no output would normally have been printed. The scanning of every file will stop on the first match.'
        )
        parser.add_argument(
            '-l',
            '--files-with-matches',
            dest='files_with_matches',
            action='store_true',
            default=False,
            help=
            'Suppress normal output; instead print the name of each input file from which output would normally have been printed. The scanning of every file will stop on the first match.'
        )
        parser.add_argument(
            '-m',
            '--max-count',
            dest='max_count',
            action='store',
            type=int,
            default=-1,
            help=
            'Stop reading a file after num matching lines. If the input is standard input from a regular file, and num matching lines are output, grep ensures that the standard input is positioned just after the last matching line before exiting, regardless of the presence of trailing context lines. This enables a calling process to resume a search.'
        )
        parser.add_argument(
            '-o',
            '--only-matching',
            dest='only_matching',
            action='store_true',
            default=False,
            help=
            'Print only the matched (non-empty) parts of matching lines, with each such part on a separate output line.'
        )
        parser.add_argument(
            '-q',
            '--quiet',
            dest='quiet',
            action='store_true',
            default=False,
            help=
            'Quiet; do not write anything to standard output. Exit immediately with zero status if any match is found, even if an error was detected.'
        )
        parser.add_argument(
            '-s',
            '--no-message',
            dest='no_message',
            action='store_true',
            default=False,
            help=
            'Suppress error messages about nonexistent or unreadable files.')
        # Output Line Prefix
        parser.add_argument(
            '-b',
            '--byte-offset',
            dest='byte_offset',
            action='store_true',
            default=False,
            help=
            'Print the 0-based byte offset within the input file before each line of output. If ‘-o’ (‘--only-matching’) is specified, print the offset of the matching part itself. '
        )
        parser.add_argument(
            '-H',
            '--with-filename',
            dest='with_filename',
            action='store_true',
            default=False,
            help=
            'Print the file name for each match. This is the default when there is more than one file to search.'
        )
        parser.add_argument(
            '-h',
            '--no-filename',
            dest='no_filename',
            action='store_true',
            default=False,
            help=
            'Suppress the prefixing of file names on output. This is the default when there is only one file (or only standard input) to search.'
        )
        parser.add_argument(
            '--label',
            dest='label',
            action='store',
            help=
            'Display input actually coming from standard input as input coming from file LABEL.'
        )
        parser.add_argument(
            '-n',
            '--line-number',
            dest='line_number',
            action='store_true',
            default=False,
            help=
            'Prefix each line of output with the 1-based line number within its input file.'
        )
        parser.add_argument(
            '-T',
            '--initial-tab',
            dest='initial_tab',
            action='store_true',
            default=False,
            help=
            'Make sure that the first character of actual line content lies on a tab stop, so that the alignment of tabs looks normal. This is useful with options that prefix their output to the actual content: ‘-H’, ‘-n’, and ‘-b’. In order to improve the probability that lines from a single file will all start at the same column, this also causes the line number and byte offset (if present) to be printed in a minimum-size field width. '
        )
        parser.add_argument(
            '-u',
            '--unix-byte-offsets',
            dest='unix_byte_offsets',
            action='store_true',
            default=False,
            help='Report Unix-style byte offsets.')
        parser.add_argument(
            '-Z',
            '--null',
            dest='null',
            action='store_true',
            default=False,
            help=
            'Output a zero byte (the ASCII NUL character) instead of the character that normally follows a file name.'
        )
        # Context Line Control
        parser.add_argument(
            '-A',
            '--after-context',
            dest='after_context',
            action='store',
            default=0,
            type=int,
            help='Print num lines of trailing context after matching lines.')
        parser.add_argument(
            '-B',
            '--before-context',
            dest='before_context',
            action='store',
            default=0,
            type=int,
            help='Print num lines of leading context before matching lines.')
        parser.add_argument(
            '-C',
            '--context',
            dest='context',
            action='store',
            default=0,
            type=int,
            help='Print num lines of leading and trailing output context.')
        # File and Directory Selection
        parser.add_argument(
            '-a',
            '--text',
            dest='text',
            action='store_true',
            default=False,
            help=
            'Process a binary file as if it were text; this is equivalent to the ‘--binary-files=text’ option. '
        )
        parser.add_argument(
            '--binary-files',
            dest='binary_files',
            action='store',
            help=
            'If the first few bytes of a file indicate that the file contains binary data, assume that the file is of type type. By default, type is ‘binary’, and grep normally outputs either a one-line message saying that a binary file matches, or no message if there is no match. If type is ‘without-match’, grep assumes that a binary file does not match; this is equivalent to the ‘-I’ option. If type is ‘text’, grep processes a binary file as if it were text; this is equivalent to the ‘-a’ option. Warning: ‘--binary-files=text’ might output binary garbage, which can have nasty side effects if the output is a terminal and if the terminal driver interprets some of it as commands. '
        )
        parser.add_argument(
            '-D',
            '--devices',
            dest='devices',
            action='store',
            help=
            'If an input file is a device, FIFO, or socket, use action to process it. By default, action is ‘read’, which means that devices are read just as if they were ordinary files. If action is ‘skip’, devices, FIFOs, and sockets are silently skipped. '
        )
        parser.add_argument(
            '-d',
            '--directories',
            dest='directories',
            action='store',
            help=
            'If an input file is a directory, use action to process it. By default, action is ‘read’, which means that directories are read just as if they were ordinary files (some operating systems and file systems disallow this, and will cause grep to print error messages for every directory or silently skip them). If action is ‘skip’, directories are silently skipped. If action is ‘recurse’, grep reads all files under each directory, recursively; this is equivalent to the ‘-r’ option. '
        )
        parser.add_argument(
            '--exclude',
            dest='exclude',
            action='append',
            help=
            'Skip files whose base name matches glob (using wildcard matching). A file-name glob can use ‘*’, ‘?’, and ‘[’...‘]’ as wildcards, and \ to quote a wildcard or backslash character literally. '
        )
        parser.add_argument(
            '--exclude-from',
            dest='exclude_from',
            action='append',
            help=
            'Skip files whose base name matches any of the file-name globs read from file (using wildcard matching as described under ‘--exclude’). '
        )
        parser.add_argument(
            '--exclude-dir',
            dest='exclude_dir',
            action='append',
            help=
            'Exclude directories matching the pattern dir from recursive directory searches. '
        )
        parser.add_argument(
            '-I',
            dest='I',
            action='store_true',
            default=False,
            help=
            'Process a binary file as if it did not contain matching data; this is equivalent to the ‘--binary-files=without-match’ option. '
        )
        parser.add_argument(
            '--include',
            dest='include',
            action='append',
            help=
            'Search only files whose base name matches glob (using wildcard matching as described under ‘--exclude’). '
        )
        parser.add_argument(
            '-r',
            '--recursive',
            dest='recursive',
            action='store_true',
            default=False,
            help=
            'For each directory mentioned on the command line, read and process all files in that directory, recursively. This is the same as the ‘--directories=recurse’ option. '
        )
        # Other Options
        parser.add_argument(
            '--line-buffered',
            dest='line_buffered',
            action='store_true',
            default=False,
            help=
            'Use line buffering on output. This can cause a performance penalty. '
        )
        parser.add_argument(
            '--mmap',
            dest='mmap',
            action='store_true',
            default=False,
            help=
            'If possible, use the mmap system call to read input, instead of the default read system call. In some situations, ‘--mmap’ yields better performance. However, ‘--mmap’ can cause undefined behavior (including core dumps) if an input file shrinks while grep is operating, or if an I/O error occurs. '
        )
        parser.add_argument(
            '-U',
            '--binary',
            dest='binary',
            action='store_true',
            default=False,
            help=
            'Treat the file(s) as binary. By default, under MS-DOS and MS-Windows, grep guesses the file type by looking at the contents of the first 32kB read from the file. If grep decides the file is a text file, it strips the CR characters from the original file contents (to make regular expressions with ^ and $ work correctly). Specifying ‘-U’ overrules this guesswork, causing all files to be read and passed to the matching mechanism verbatim; if the file is a text file with CR/LF pairs at the end of each line, this will cause some regular expressions to fail. This option has no effect on platforms other than MS-DOS and MS-Windows. '
        )
        parser.add_argument(
            '-z',
            '--null-data',
            dest='null_data',
            action='store_true',
            default=False,
            help=
            'Treat the input as a set of lines, each terminated by a zero byte (the ASCII NUL character) instead of a newline. Like the ‘-Z’ or ‘--null’ option, this option can be used with commands like ‘sort -z’ to process arbitrary file names. '
        )
        # Encoding Options
        parser.add_argument(
            '-E',
            '--encoding',
            dest='encoding',
            action='append',
            help='Encoding for reading text files.')
        parser.add_argument(
            '-G',
            '--guess',
            dest='guess',
            action='store_true',
            default=False,
            help='Guess encoding for text files.')
        options = parser.parse_args()
        if options.help:
            parser.print_help()
            parser.exit()
        elif options.version:
            print('Version: 0.1')
            parser.exit()
        else:
            return options


if __name__ == '__main__':
    x = EncodingGrep()
