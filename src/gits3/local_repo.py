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


remote_ref = 'refs/remotes/s3/master'

class Gits3(object):

    def __init__(self, path):
        self.path = path

    def open_repo(self, path):
        return Repo(path)
  
             
    def get_updates(self, local_ref):
        
        repo = self.open_repo(self.path)        
        
        refs = repo.get_refs()
        for key, value in refs.iteritems():
           print key, value
        
        local = refs[local_ref]
        remote = refs[remote_ref]
        
        
        local_object = repo.get_object(local)
        remote_object = repo.get_object(remote)
        
        
        commits = self.get_commits(repo, local_object, [remote])
        objects = self.get_objects(repo, commits)
#        print objects
        
        objects = set(objects)
        return objects
        
       
       
        # os = repo.object_store
        # remote_wlkr = repo.get_graph_walker(repo.refs.as_dict('refs/remotes/s3').values())
        # local_wlkr = repo.get_graph_walker()
        
        # result = os.generate_pack_contents([local_object.sha()], [remote_object.sha()])
        
        
        
    def get_commits(self, repo, interesting, uninteresting):
        commits = [interesting]
        remaining = interesting.get_parents()
        
        while remaining:
            pId = remaining.pop(0)
            if pId in uninteresting:
                continue    
            else:
                parent = repo.get_object(pId)
                commits.append(parent)
                parents = parent.get_parents()
                remaining.extend(parents)
        return commits
    
    
    def get_objects(self, repo, commits):
        objects = []
        while commits:
            commit = commits.pop(0)
            objects.append(commit)
            objects.extend(self.get_objects_in_tree(repo, commit.tree))
        return objects    
            
            
    
    def get_objects_in_tree(self, repo, treeId):
        objects = []
        tree = repo.get_object(treeId)
        objects.append(tree)
        entries = tree.entries()
        for entryId in entries:
            # get the entry's sha 
            objectId = entryId[2]
            object = repo.get_object(objectId) 
            if isinstance(object, Tree):
                objects.extend(self.get_objects_in_tree(repo, objectId))
            else:
                objects.append(object)    
        return objects
      
    def generate_pack_name(self, objects):
        m = hashlib.sha1()
        for object in objects:
            sha1 = object.sha().hexdigest()
            print sha1
            m.update(sha1)
        file_name = m.hexdigest()
        print 'File Name is ', file_name
        return file_name
    
    
    def write_pack(self, pack_name, objects):
         write_pack('pack-' + pack_name, [(x, "") for x in objects], 
            len(objects))
        