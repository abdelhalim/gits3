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

import hashlib

from dulwich.objects import ( 
    Blob,
    Tree,
    Commit,
    Tag,
    )

from dulwich.pack import (
    Pack,
    PackData,
    write_pack,
    )

from dulwich.repo import Repo

from dulwich.object_store import (
    DiskObjectStore,
    BaseObjectStore,
    ObjectStoreGraphWalker,
    )



class Gits3(object):

    def __init__(self, path):
        self.path = path
        self.open_repo(path)

    def open_repo(self, path):
        self.repo = Repo(path)
  
    def get_id(self, ref):
        return self.repo.get_refs()[ref]
             
    def get_updates(self, local_ref, tracking_ref):        
        
                
        refs = self.repo.get_refs()
        for key, value in refs.iteritems():
           print key, value
        
        local = refs[local_ref]
        try:
            remote = refs[tracking_ref]
        except KeyError:
            remote = None
            
        
        if local == remote:
            return None
        
        local_object = self.repo.get_object(local)
        
        
        commits = self.get_commits(local_object, [remote])
        objects = self.get_objects(commits)
        print objects
        
        if remote:
            remote_object = self.repo.get_object(remote)
            filtered_objects = self.filter_objects(objects, remote_object)
        else:
            filtered_objects = objects
        
        filtered_objects = set(filtered_objects)
        return filtered_objects
        
        
    def filter_objects(self, objects, old_commit):
        filtered = []
        old_treeId = old_commit.tree
        old_objects = self.get_objects_in_tree(old_treeId)
        for object in objects:
            if object not in old_objects:
                filtered.append(object)
                
        return filtered
        
    def get_commits(self, interesting, uninteresting):
        commits = [interesting]
        remaining = interesting.get_parents()
        
        while remaining:
            pId = remaining.pop(0)
            if pId in uninteresting:
                continue    
            else:
                parent = self.repo.get_object(pId)
                commits.append(parent)
                parents = parent.get_parents()
                remaining.extend(parents)
        return commits
    
    
    def get_objects(self, commits):
        objects = []
        while commits:
            commit = commits.pop(0)
            objects.append(commit)
            objects.extend(self.get_objects_in_tree(commit.tree))
        return objects    
            
            
    
    def get_objects_in_tree(self, treeId):
        objects = []
        tree = self.repo.get_object(treeId)
        objects.append(tree)
        entries = tree.entries()
        for entryId in entries:
            # get the entry's sha 
            objectId = entryId[2]
            object = self.repo.get_object(objectId) 
            if isinstance(object, Tree):
                objects.extend(self.get_objects_in_tree(objectId))
            else:
                objects.append(object)    
        return objects
      
    def generate_pack_name(self, objects):
        m = hashlib.sha1()
        for object in objects:
            sha1 = object.sha().hexdigest()
#            print sha1
            m.update(sha1)
        file_name = m.hexdigest()
#        print 'File Name is ', file_name
        return file_name
    
    
    def write_pack(self, pack_name, objects):
         write_pack('pack-' + pack_name, [(x, "") for x in objects], 
            len(objects))
        
    def find_tracking_ref_names(self, fetch, refs):
        if fetch[0] == '+':
            fetch = fetch[1:]
        tmp = fetch.split(':')
        src = tmp[0]
        dst = tmp[1]
        
        # TODO double check that both src and dst have wild cards, or both don't
        
        # match the source with refs
        if src.endswith('*') and refs.startswith(src[:-1]):
            return self.expand_from_src(src, dst, refs)
        else:
            return dst                                         
            
        
    def expand_from_src(self, src, dst, refs):
        return dst[:-1] + refs[len(src)-1:]