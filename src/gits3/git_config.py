
'''

Most of the contents of class GitConfigParser is a copy of the Python ConfigParser.py with 
minor modification:

- Remove line continuation support
- Modify the regex to support git subsections
 

'''

DEFAULTSECT = "DEFAULT"

from ConfigParser import ConfigParser
import re
import os


class GitConfig:
    def __init__(self, root):
        self.config_file = os.path.join(root, ".git", "config")

        self.cfg = GitConfigParser()
        self.cfg.read(self.config_file)


    def get_remote_url(self):
        
        url = self.cfg.get('remote', 'url')
        return url

    def get_fetch(self):
        fetch = self.cfg.get('remote', 'fetch')
        return fetch
        
class GitConfigParser(ConfigParser):
    
    
    def __init__(self):
        
        ConfigParser.__init__(self)
         
        #
        # Regular expressions for parsing section headers and options.
        #
        self.SECTCRE = re.compile(
            r'\['                                 # [
            r'(?P<header>[^]\s\.]+)\s*'              # very permissive!
            r'(\"(?P<sub_section>[\w]+)\")?'      # very permissive!
            r'\]'                                 # ]
            )
        self.OPTCRE = re.compile(
            r'\s*(?P<option>[^:=\s][^:=]*)'       # very permissive!
            r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                                  # followed by separator
                                                  # (either : or =), followed
                                                  # by any # space/tab
            r'(?P<value>.*)$'               # everything up to eol
            )
              
    def _read(self, fp, fpname):
        """Parse a sectioned setup file.

        The sections in setup file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name: value' format lines.
        Continuations are represented by an embedded newline then
        leading whitespace.  Blank lines, lines beginning with a '#',
        and just about everything else are ignored.
        """
        cursect = None                            # None, or a dictionary
        optname = None
        lineno = 0
        e = None                                  # None, or an exception
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == DEFAULTSECT:
                        cursect = self._defaults
                    else:
                        cursect = {'__name__': sectname}
                        self._sections[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if vi in ('=', ':') and ';' in optval:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = optval.find(';')
                            if pos != -1 and optval[pos-1].isspace():
                                optval = optval[:pos]
                        optval = optval.strip()
                        # allow empty values
                        if optval == '""':
                            optval = ''
                        optname = self.optionxform(optname.rstrip())
                        cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

