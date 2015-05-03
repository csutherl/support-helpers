#!/usr/bin/env python

""" Command to parse high-cpu output and find threads consuming large amounts of CPU, then correlate
that CPU info to Java thread info. """

import sys
import datetime
import re
import math

import pprint
pp = pprint.PrettyPrinter(indent=4)

__author__ = "coty"

def parseTop():
    # cpu_threshold is set a the CPU percentage that you consider high
    # process usage will only be recorded if its greater than cpu_threshold
    cpu_threshold = 20
    cpudata = {}

    # filename = sys.argv[1]
    filename = 'high-cpu.out'

    print("Reading %s" % filename)
    with open(filename) as f:
        content = f.readlines()
        counter = 0
        currentRun = {}
        processes = []
        oldDate = datetime.datetime(1970, 1, 1)
        newDate = None

        for ns_line in content:
            line = ns_line.strip()
            # grab a date, if it isn't a date, skip this code
            try:
                #print(line)
                newDate = datetime.datetime.strptime(line, '%a %b %d %H:%M:%S %Z %Y')
             
                if newDate > oldDate:
                    currentRun['processes'] = processes
                    # cpudata[counter] = currentRun
                    cpudata[newDate] = currentRun
                    # counter += 1
                    currentRun = {}
                    processes = []
                    oldDate = newDate
            
                if 'date' not in currentRun.keys(): 
                    currentRun['date'] = line.strip()

                continue
            except ValueError:
                pass

            # check the line for other top data before the process lines
            if line.startswith('top'):
                # top - 14:24:13 up 4 days, 18:36, 13 users,  load average: 1.79, 1.68, 1.60
                # grabbing uptime
                currentRun['uptime'] = re.search('up[\s0-9a-zA-Z]+', line).group(0)
                # grabbing ldavg data
                ldavg_match = re.search('load average: ([0-9]+.[0-9]+), ([0-9]+.[0-9]+), ([0-9]+.[0-9]+)', line)
                currentRun['ldavg'] = {'1 min': ldavg_match.group(1), '5 min': ldavg_match.group(2), '15 min': ldavg_match.group(3)}
                continue
            if line.startswith('Tasks') or line.startswith('Threads'):
                # Tasks: 186 total,   1 running, 185 sleeping,   0 stopped,   0 zombie ## RHEL
                # Threads:  41 total,   0 running,  41 sleeping,   0 stopped,   0 zombie ## Fedora
                currentRun['Tasks'] = re.search('([0-9]+ total)', line).group(1)
                continue
            if line.startswith('Cpu'):
                # Cpu(s): 17.9%us,  1.3%sy,  0.0%ni, 80.3%id,  0.3%wa,  0.0%hi,  0.2%si,  0.0%st
                usg = re.search('([0-9]+.[0-9]+%)us', line).group(1)
                syg = re.search('([0-9]+.[0-9]+%)sy', line).group(1)
                idg = re.search('([0-9]+.[0-9]+%)id', line).group(1)
                currentRun['Cpu'] = {'us': usg, 'sy': syg, 'id': idg}
                continue
            if line.startswith('Mem'):
                # Mem:  28822876k total, 22717528k used,  6105348k free,   874212k buffers ## RHEL
                mem_match = re.search('([0-9]+)k total,\s+([0-9]+)k used', line)
                totalMem = mem_match.group(1)
                usedMem = mem_match.group(2)
                percentUsed = int(math.ceil((float(usedMem) / float(totalMem)) * 100))
                currentRun['Mem'] = "%s%% used" % percentUsed
                continue
            if line.startswith('KiB Mem'):
                # KiB Mem:  16127716 total, 15760052 used,   367664 free,   374676 buffers ## Fedora
                mem_match = re.search('([0-9]+) total,\s+([0-9]+) used', line)
                totalMem = mem_match.group(1)
                usedMem = mem_match.group(2)
                percentUsed = int(math.ceil((float(usedMem) / float(totalMem)) * 100))
                currentRun['Mem'] = "%s%% used" % percentUsed
                continue
            if line.startswith('KiB Swap'):
                # KiB Swap:  8134652 total,  1218992 used,  6915660 free,  4380324 cached
                swap_match = re.search('([0-9]+) total.*([0-9]+) used', line)
                totalSwap = swap_match.group(1)
                usedSwap = swap_match.group(2)
                percentUsed = int(math.ceil((float(usedSwap) / float(totalSwap)) * 100))
                currentRun['Swap'] = "%s%% used" % percentUsed
                continue
            if line.startswith('Swap'):
                # Swap:  1048572k total,    48252k used,  1000320k free,  3801500k cached
                swap_match = re.search('([0-9]+)k total.*([0-9]+)k used', line)
                totalSwap = swap_match.group(1)
                usedSwap = swap_match.group(2)
                percentUsed = int(math.ceil((float(usedSwap) / float(totalSwap)) * 100))
                currentRun['Swap'] = "%s%% used" % percentUsed
                continue
            if len(line) == 0 or line.startswith('PID'):
                #  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND
                # skip the header line or blank lines
                continue
    
            # 60131 jboss     20   0 6023m 2.6g  19m S  0.0  9.5   0:00.00 /opt/jboss/java/bin/java -D[Server:myl-3-b] -XX:PermSize=256m -X
            # grab CPU data and parse out things we care about
            words = line.split()
            # check formatting of line
            if len(words) < 12:
                print("ERROR: words array not long enough")
                print("HINT: TZ may not work.")
                print("ERROR LINE: %s" % line)
                sys.exit()
    
            if 'java' in words[11]:
                pid = words[0]
                cpu = float(words[8])
                if cpu >= cpu_threshold:
                    processes.append({'pid': pid, 'hexpid': hex(int(pid)), 'cpu': cpu, 'mem': words[9]})
    
        # to catch the last run, save the structs from the last run
        currentRun['processes'] = processes
        # cpudata[counter] = currentRun
        cpudata[newDate] = currentRun
        
        # my brain is broke today
        # del cpudata[0]
        print("Done reading file")
    
    # now that the data has been parsed, read through and find PIDs that exist in multiple dumps
    # iterate over all pids and add them to a dict where the key is the pid and the values are the dumps it came from
    # if there are len(dumps) > 1, then it showed up in multiple and we want to record the thread dumps from those dumps
    # for that pid
    seen = {}
    for dump in cpudata:
        for proc in cpudata[dump]['processes']:
            hexpid = proc['hexpid']
            if dump not in seen.keys():
                seen[dump] = [hexpid]
            else:
                dumps = seen[dump]
                dumps.append(hexpid)
                seen[dump] = dumps
    
    # return seen
    return cpudata
  
def parseThreadDumps(): 
    # stack meta will be keyed on date
    stack_meta = {}
    
    # filename = sys.argv[1]
    filename = 'high-cpu-tdump.out'

    print("Reading %s" % filename)
    with open(filename) as f:
        content = f.readlines()
        # stacks will be keyed on the nid
        stacks = {}
        stack_id = 0
        oldDate = datetime.datetime(1970, 1, 1)
    
        for ns_line in content:
            line = ns_line.strip()
            
            # skip any lines that start with dates or "Full thread" as they aren't useful
            if re.match('^201[0-9]+-', line) or re.match('^Full thread', line) or re.match('^$', line): 
                continue
    
            try:
                newDate = datetime.datetime.strptime(line, '%a %b %d %H:%M:%S %Z %Y')
    
                if newDate > oldDate:
                    stack_meta[newDate] = stacks
                    oldDate = newDate
    
                continue
            except ValueError:
                pass
    
            if (line.startswith('"')):
                stack_id = re.search('nid=(0x[0-9a-zA-Z]+)', line).group(1)
                stacks[stack_id] = [line]
            else:
                stacks[stack_id].append(line)
            
    return stack_meta

def main():
    pp.pprint(parseTop())
    pp.pprint(parseThreadDumps())

main()