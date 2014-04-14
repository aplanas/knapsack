#!/usr/bin/python
# -*- coding: utf-8 -*-

#  /srv/rsync-modules/update-rsync-notify.py --src /srv/ftp-stage/pub/opensuse/ --srcalt /srv/ftp/pub/opensuse/ --dst /srv/rsync-modules/ --lists /srv/rsync-modules/result-lists/ 30g 80g 160g 320g 640g 2000g

import argparse
import os
import sys
import time
import threading

from get_path import PACKAGE

import pyinotify

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_FROM # watched events

changed_dirs = dict()

change_lock = threading.Lock()

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        self.changed(event.pathname)

    def process_IN_DELETE(self, event):
        self.changed(event.pathname)

    def process_default(self, event):
        self.changed(event.pathname)

    def changed(self, pathname):
        #print "Changed", os.path.dirname(pathname)
        change_lock.acquire()
	changed_dirs[os.path.dirname(pathname)] = time.time()
        change_lock.release()

handler = EventHandler()
notifier = pyinotify.ThreadedNotifier(wm, handler, read_freq=10)
notifier.start()

def join(path, filename):
    return os.path.join(path, filename if filename[0] != '/' else filename[1:])


def get_files(path):
    """Return the files and directories form a path."""
    files, dirs = set(), set(('/'))
    for (dirpath, dirname, filenames) in os.walk(path):
        dirpath = dirpath[len(path):]
        if dirpath:
            dirs.add(dirpath)
        files.update(os.path.join(dirpath, f) for f in filenames)
    return files, dirs


_ALL_FILES = None
def find_packages(_prefixname):
    """Use the filename_prefix to find real packages. This assumes the prefices are sorted when called"""
    res = []
    global _ALL_FILES
    all_files = _ALL_FILES
    donewith = []
    found = False
    while len(all_files):
	_basename = all_files.pop(0)
	donewith.append(_basename)
	if not _basename.startswith(_prefixname):
            # we can skip everything if we already had a prefix hit and now are no longer 
            if found: 
                # but be careful - it might be the next prefix
                all_files.insert(0, _basename)
                return res
            continue
	found = True
        _path = _basename
        m = PACKAGE.match(_basename)
	if m: _path = m.groups()[0]
        if _path.endswith(_prefixname):
            res.append(_basename)
	else:
	    # if it's not matching, the path is longer so we can stop here
	    all_files.insert(0, _basename)
	    return res
    if not found:
	_ALL_FILES = donewith
    return res

def expand_dir(_dirname, src_prefices):
    """Is called on initial setup of the all_dirs dict and later in the notify"""
    res = []
    global _ALL_FILES
    try:
      af = []
      for f in os.listdir(_dirname):
	 af.append(f.replace('-32bit', '-THIRTYTWOBITS'))
      _ALL_FILES = []
      for f in sorted(af):
        _ALL_FILES.append(f.replace('-THIRTYTWOBITS', '-32bit'))
      
    except: # if there is no such directory, we know the answer!!!
      return res
    if _dirname.endswith('/repodata'):
	fp = _ALL_FILES
	wanted_knaps = set()
	for kps in src_prefices.values():
  	  for kp in kps:
	    wanted_knaps.add(kp)
	#print "   ''", sorted(wanted_knaps), _ALL_FILES
	return [['', sorted(wanted_knaps), _ALL_FILES]]
    for prefix in sorted(src_prefices.keys()):
        fp = find_packages(prefix)
	#print "  ", prefix, src_prefices[prefix], fp
        res.append([prefix, src_prefices[prefix], fp])
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Synchronize a rsync directory using hard links and an external file.')
    parser.add_argument('--src', help='Src directory')
    parser.add_argument('--srcalt', help='Src directory')
    parser.add_argument('--dst', help='Dst directory')
    parser.add_argument('--lists', help='List directory')
    parser.add_argument('kpsol', help='Knapsack solution file', nargs='+')

    args = parser.parse_args()

    if not all((args.src, args.dst, args.kpsol)):
        parser.print_help()
        exit(0)

    args.src = os.path.abspath(args.src)
    args.srcalt = os.path.abspath(args.srcalt)
    src_files_to_expand = dict()
    for kpsol in args.kpsol:
	kp_files = sorted(f.strip() for f in open(join(args.lists, kpsol)) if f.strip())
	for file in kp_files:
            fte = src_files_to_expand.get(file, [])
            src_files_to_expand[file] = fte.append(kpsol)
	    # try: # mega python
	    #     src_files_to_expand[file].append(kpsol)
            # except KeyError:
	    #     src_files_to_expand[file] = [kpsol]

    all_dirs = dict()
    srcfiles = dict()
    currentdir = None
    for src_file in sorted(src_files_to_expand.keys()):
        _filename = join(args.src, src_file)
        _dirname, _prefixname = os.path.split(_filename)
        if _dirname != currentdir:
	   if currentdir: 
	     wm.add_watch(currentdir, mask)
             #print currentdir
	     all_dirs[currentdir[len(args.src):]] = expand_dir(currentdir, srcfiles)
           currentdir = _dirname
	   srcfiles = dict()
        srcfiles[_prefixname] = src_files_to_expand[src_file]

    args.dst = os.path.abspath(args.dst)
    args.lists = os.path.abspath(args.lists)

    wm.add_watch(args.lists, mask)

    for kpsol in args.kpsol:
	    src_dir = set(('/'))
	    src_files = set()
	    for dir, files in all_dirs.items():
		for file in files:
			if kpsol in file[1]:
				for f in file[2]:
					src_files.add(join(dir, f))
	    for src_file in src_files:
		d = os.path.dirname(src_file)
		while d != '/':
		    src_dir.add(d)
		    d = os.path.dirname(d)

	    dst_files, dst_dir = get_files(join(args.dst, kpsol))

	    # print '** SRC DIR'
	    # for i in src_dir:
	    #     print i
	    # print '** SRC FILES'
	    # for i in src_files:
	    #     print i

	    new_files = src_files - dst_files
	    del_files = dst_files - src_files

	    new_dir = src_dir - dst_dir
            cur_dir = src_dir & dst_dir
	    del_dir = dst_dir - src_dir

	    kpdir = os.path.join(args.dst, kpsol)
	    # print '** New dirs'
	    # for i in new_dir:
	    #     print i
	    if new_dir:
		print >> sys.stderr, '{1}: Creating new directories ({0})...'.format(len(new_dir), kpsol)
	    for d in sorted(new_dir):
                stat = os.stat(join(args.src, d))
		d = join(kpdir, d)
		os.mkdir(d)
                os.chmod(d, stat.st_mode)

            # Update permissions
            for d in sorted(cur_dir):
                try:
                    sd= = join(args.src, d)
                    stat = os.stat(sd)
                    d = join(kpdir, d)
                    os.chmod(d, stat.st_mode)
                except:
                    print >> sys.stderr, 'ERROR', sd, d, stat

	    # print '** New files'
	    # for i in new_files:
	    #     print i
	    if new_files:
		print >> sys.stderr, '{1}: Linking new files ({0})...'.format(len(new_files), kpsol)
	    for f in new_files:
		src, dst = join(args.src, f), join(kpdir, f)
		try:
		    os.link(src, dst)
		except:
		    #print 'SRC', src
		    #print 'DST', dst
		    src = join(args.srcalt, f)
		    try:
		       os.link(src, dst)
		    except:
                       # the initial startup is slow, so it happens that files disappear
		       # but once we're done here, we look at the notify events
		       pass 

	    # print '** Del files'
	    # for i in del_files:
	    #     print i
	    if del_files:
		print >> sys.stderr, '{1}: Unlinking deleted files ({0})...'.format(len(del_files), kpsol)
	    for f in del_files:
		f = join(kpdir, f)
		os.unlink(f)

	    # print '** Del dirs'
	    # for i in del_dir:
	    #     print i
	    if del_dir:
		print >> sys.stderr, '{1}: Unlinking deleted directories ({0})...'.format(len(del_dir), kpsol)
	    for d in sorted(del_dir, reverse=True):
		d = join(kpdir, d)
		os.rmdir(d)
 
    print "looping"
    while not changed_dirs.has_key(args.lists):
      dirtoupdate = None
      change_lock.acquire()
      for dir in changed_dirs:
         if time.time() - changed_dirs[dir] < 100: continue
         del changed_dirs[dir]
	 dirtoupdate = dir[len(args.src):]
         break
      change_lock.release()
      if not dirtoupdate:
        print "sleep 20"
        time.sleep(20)
        continue
      #update_dir(dirs)
      
      if not all_dirs.has_key(dirtoupdate):
         print "not found:", dirtoupdate, sorted(all_dirs.keys())
         continue

      print "updating", dirtoupdate
      #print "B:", dirtoupdate, all_dirs[dirtoupdate]
      # collect the prefices in all knapsacks
      srcfiles = dict()
      for src_file in all_dirs[dirtoupdate]:
        srcfiles[src_file[0]] = src_file[1]
      all_dirs[dirtoupdate] = expand_dir(join(args.src, dirtoupdate), srcfiles)
      #print "A:", dirtoupdate, all_dirs[dirtoupdate]

      # update knapsacks
      for kpsol in args.kpsol:
        kpdir = join(os.path.join(args.dst, kpsol), dirtoupdate)
        src_files = set()
        for file in all_dirs[dirtoupdate]:
          if kpsol in file[1]:
            for f in file[2]:
              src_files.add(f)
        dst_files, dst_dir = get_files(kpdir)
        new_files = src_files - dst_files
        del_files = dst_files - src_files
	#print kpsol, src_files, dst_files, new_files, del_files
        # TODO: avoid code duplication
        if del_files:
           print >> sys.stderr, '{1}: Unlinking deleted files ({0})...'.format(len(del_files), kpsol)
        for f in del_files:
           f = os.path.join(kpdir, f)
           os.unlink(f)

        if new_files:
          print >> sys.stderr, '{1}: Linking new files ({0})...'.format(len(new_files), kpsol)
        for f in new_files:
          src, dst = os.path.join(join(args.src, dirtoupdate), f), os.path.join(kpdir, f)
          try:
            os.link(src, dst)
          except:
            #print 'SRC', src
            #print 'DST', dst
            src = os.path.join(join(args.srcalt, dirtoupdate), f)
            try:
              os.link(src, dst)
            except:
              print "linking failed", f, dirtoupdate, kpsol
              pass

    notifier.stop()
