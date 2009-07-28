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
from s3_push import Gits3

if __name__ == '__main__':
    
    client = Gits3()
    
    updated_objects = client.get_updates()
    
    pack_name = client.generate_pack_name(updated_objects)
    
    client.write_pack(pack_name, updated_objects)
    
    pass