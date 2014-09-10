# DayOne Task Extractor
# Harvest tasks written in Day One, and write them to TaskPaper
#Note: depends on lxml (pip install lxml) version = 3.3.1

from datetime import date, datetime, tzinfo, timedelta, time
import os, sys
import ConfigParser
from lxml import etree

output_file = "~/Dropbox/Documents/TaskPaper/foundtasks.taskpaper"
dayone_directory = "~/Dropbox/Apps/Day One/Journal.dayone/entries"
ini_file = 'taskextractor.ini'


output_file = os.path.expanduser(output_file)

#Used to sort the directories in the last modified order
#http://stackoverflow.com/questions/4500564/directory-listing-based-on-time
def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime, reverse=True))
    
def newly_modified_files(last_run_time):
    n = 0;
    files = sorted_ls(os.path.expanduser(dayone_directory))
    for fl in files:
        raw_mod_time = os.path.getmtime(os.path.join(os.path.expanduser(dayone_directory),fl))
        mod_time = datetime.utcfromtimestamp(raw_mod_time)
        if mod_time < last_run_time:
            break
        n=n+1
    return files[0:n]

def read_element_value( root, xpath_selector ):
    #http://lxml.de/xpathxslt.html
    find_node = etree.XPath(xpath_selector)
    found_node = find_node(root)
    
    if len(found_node) == 0:
    	return ""
    
    #print "NODE SLELECTED WITH {0}".format(xpath_selector)
    thevalue =found_node[0].text
    
    return thevalue

def process_new_entries_since(last_run_time, new_task_function):
    for fl in newly_modified_files(last_run_time):
        try:
            #For debugging, showing the file
            mod_time = datetime.utcfromtimestamp(os.path.getmtime(os.path.join(os.path.expanduser(dayone_directory),fl)))
            print fl, datetime.strftime(mod_time, "%b %d %Y %H:%M")
            
            entry_file = open(os.path.join(os.path.expanduser(dayone_directory),fl), 'rb')
            #(Why didn't DayOne be nice and do <key item=""UUID"> or even <UUID>xxx</UUID> Grrr!!!

        
            tree = etree.parse( entry_file )
            #uuid = read_element_value( tree, "//key[text()='UUID']/../string")
            body = read_element_value( tree, "//key[text()='Entry Text']/../string")
        
            #Now, extract only lines that begin with @ and isn't already @done
            for line in body.split("\n"):
                if line.lstrip().startswith("@"):
                    if "@done" not in line.lower():
                        new_task_function(fl, line)
        except:
            print "Error parsing lines"
            print entry_file
            print "Unexpected error:", sys.exc_info()
                    
def print_found_entries(fl, line):
    print "[{0}](dayone://edit?entryId={1})".format(line.trim(), fl.replace(".doentry",""))

def append_found_entries(fl, line):	
    try:
        # if line is None:
        #     return

        line = line.strip()
        task_file = open(output_file, 'a')
        
        sep = line.split(" ")
        context = sep[0]
        task = line[len(context)+1:]
            
        link = fl.replace(".doentry","")
        
        task_file.write("- {0} [{1}]()\n\t[{1}]: dayone://edit?entryId={2}\n\n".format(context, task, link))
        task_file.close()
        
        #print "[{0}](dayone://edit?entryId={1})".format(line, fl.replace(".doentry",""))
    except:
        print "Error appending from {1} to file {0}".format(output_file, fl)
        print "Unexpected error:", sys.exc_info()


def get_last_run(harvester):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    if 'last_run' not in config.sections():
        cfg = open(ini_file,'w')
        config.add_section('last_run')
        config.write(cfg)
        cfg.close()
    
    try:
    	lr = config.get('last_run', harvester)
    except ConfigParser.NoOptionError:
    	print "No default set"
        lr= 'Jan 1 1970 12:00'

    return datetime.strptime(lr, "%b %d %Y %H:%M")
        
def set_last_run(harvester):
    config = ConfigParser.ConfigParser()
    config.read(ini_file)
    
    cfg = open(ini_file,'w')
    last_run = config.set('last_run', harvester, datetime.now().strftime("%b %d %Y %H:%M"))
    config.write(cfg)
    cfg.close()


#Read all Day One entries since the last run
#last_run_time = datetime.strptime(last_run, "%b %d %Y %H:%M")

last_run_time = get_last_run('day_one')
print "Checking files modified since {0}".format(last_run_time)
process_new_entries_since(last_run_time, append_found_entries)
set_last_run('day_one')

