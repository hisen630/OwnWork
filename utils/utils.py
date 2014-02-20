#!/usr/bin/env python2.7
#coding=utf-8

import sys
import os
import datetime, re, subprocess

HADOOP_CLIENT = '/home/work/hadoop-client/hadoop/bin/hadoop'

def remove_data(cur_path):
    """
    remove a HDFS path
    """
    cmd = "%s dfs -rmr %s"%(HADOOP_CLIENT, cur_path)
    print cmd
    os.system(cmd)

def list_date(start_date_str, end_date_str, max_range=10240):
    """
    return a list of date-str from start_date to end_date(exclusively)
    """
    year, month, day = map(int, (start_date_str[:4],
                                 start_date_str[4:6],
                                 start_date_str[6:]))
    base_date = datetime.date(year, month,day)
    date_list = []
    for i in range(0, max_range):
        date = base_date + datetime.timedelta(days=i)
        date = re.sub("-","",str(date))
        if date == end_date_str:
            break
        date_list.append(date)
    return date_list

def paral_run(cmd_list, p_level):
    """
    Run parallel jobs.
    param:
        cmd_list - the cmd-str list
        p_level - an int, how many subprocesses to run.
    """
    for i in range(0, len(cmd_list), p_level):
        print "[Group %d]"%i

        exe_cmds = []
        pid_list = []
        for j in range(i, i+p_level):
            if j < len(cmd_list):
                exe_cmds.append(cmd_list[j])
                print cmd_list[j]
        for idx, cmd in enumerate(exe_cmds):
            pid = subprocess.Popen(cmd, shell=True)
            pid_list.append(pid)

        # wait for all the sub process
        for idx, pid in enumerate(pid_list):
            pid.wait()
