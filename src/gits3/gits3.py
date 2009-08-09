# Copyright (C) 2009 Abdelhalim Ragab <abdelhalim@gmail.com>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 3
# of the License or (at your option) any later version of 
# the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''
Created on Jul 10, 2009

@author: abdelhalim
'''
from local_repo import Gits3
from git_config import GitConfig
from amazon_s3_transport import S3Transport

import os
import sys
import getopt



def usage():
    print 'Usage: gits3 push <remote> <refs>'


def main(argv):
    
    
    # parse the arguments
    
    try:
        opts, args = getopt.getopt(argv, 'h')
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    if len(args) < 3:
        usage()
        sys.exit(2)
    if args[0] != 'push':
        usage()
        sys.exit(2)    
    
    refs = args[2]
    print 'Local Refs: ',refs 
        
        
    # get current directory
    root = os.getcwd()
    # TODO Add check to see if the current folder is Git repo
    
    cfg = GitConfig(root)
    url = cfg.get_remote_url()
    transport = S3Transport(url)
    

    client = Gits3(root)
    
    updated_objects = client.get_updates(refs)
    
    base = client.generate_pack_name(updated_objects)
    
    client.write_pack(base, updated_objects)
    
    pack_name = 'pack-' + base + '.pack'
    transport.upload_pack(pack_name)
    transport.upload_pack('pack-' + base + '.idx')
    
    packs = transport.get_pack_names()
    packs_str = 'P ' + pack_name + '\n'
    for pack in packs:
        packs_str = packs_str + 'P ' + pack + '\n'
    
    print packs_str
    
    pass


if __name__ == '__main__':
    main(sys.argv[1:])