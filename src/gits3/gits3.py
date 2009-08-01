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


if __name__ == '__main__':
    
    # should get current directory
    root = '/Users/abdelhalim/dev/remote_git/scratch'
    cfg = GitConfig(root)
    url = cfg.get_remote_url()
    transport = S3Transport(url)
    print transport.get_pack_names()

    client = Gits3()
    
    updated_objects = client.get_updates()
    
    pack_name = client.generate_pack_name(updated_objects)
    
    client.write_pack(pack_name, updated_objects)
    
    transport.upload_pack('pack-' + pack_name + '.pack')
    transport.upload_pack('pack-' + pack_name + '.idx')
    
    
    
    
    pass