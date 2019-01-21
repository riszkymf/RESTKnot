import os
import sys
from .base import Base
from libs import utils as util
from libs import config as app
from libs import remove as delete
from libs import list as ls
from libs.auth import check_password
from libs.wrapper import *
from tabulate import tabulate

class Rm(Base):
    """
    usage:
        rm dns (--nm NAME)
        rm record [(--nm-zone=ZNNAME [--nm-record=NAME] [--type=TYPE] )]

    Options :
        -h --help               Print usage
        --nm=NAME               DNS' name to delete
        --nm-record=NAME        Filter record by record's name
        --nm-zn=ZNNAME          Filter record by zone's name

    Commands:
     ttl                        List available ttl
     type                       List available type 
    
    """
    def execute(self):
        if self.args['dns']:
            zone = [self.args['--nm']]
            util.log_warning('The following record will also be deleted\n')
            listdns = ls.list_record(zone)
            listdns = util.table_cleanup(listdns)
            print(tabulate(listdns,headers="keys",tablefmt="rst"))
            if util.assurance() and check_password():
                delete.remove_zone(zone[0])
            else:
                exit()
        elif self.args['record']:
            if self.args['--nm-zone']:
                id_record = list()
                zone = [self.args['--nm-zone']]
                tags = self.args
                show = list()
                show = ls.list_record(zone,tags)

            else:
                zone = ls.list_dns()
                show = ls.list_record(zone)
                id_record = list()
            for row in show:
                row = util.dictcleanup(row)
                id_record.append(row['id_record'])
            if(len(show)>0):
                show = util.table_cleanup(show)
                print(tabulate(show, headers="keys" ,showindex="always",tablefmt="rst"))
                try : 
                    index = raw_input("""
Type the index of the record (0~{}), if you want to remove multiple record
separate the index using comma (,)
""".format(len(show)-1))
                except :
                    print("Invalid Input")
                else :
                    index = index.split(',')
                    index = util.check_availability(index,(len(show)-1))
                    sendid = list()
                    for i in index:
                        sendid.append(id_record[int(i)])
                    util.log_warning('Removing record is irreversible, are you sure ?\n')
                    if util.assurance() and check_password():
                        delete.remove_record(sendid)
                    else:
                        exit()                    
