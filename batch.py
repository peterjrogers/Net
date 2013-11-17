from tools import Tools
from mnet3 import Mnet
import session3, vty, time

class Batch(Tools, Mnet):
    def __init__(self, dev_con, cli_con):
        Tools.__init__(self)
        Mnet.__init__(self)
        
        """
        Batch processing tools
        
        (c) 2012, 2013 Intelligent Planet Ltd
        """
        
        self.clear()
        self.dev_con = dev_con
        self.cli_con = cli_con
        self.out_file = 'c:/batch'
        self.time_wait = 1
    
    
    def clear(self): 
        self.batch_host_list = []
        
        
    def list_format(self, clist):
        try: clist.sort()
        except: clist = [clist]
        finally: return clist
    
    
    def insert(self, view_list):
        
        view_list = self.list_format(view_list)
        
        for host in view_list:
            if host not in self.batch_host_list: 
                print host.upper()
                self.batch_host_list.append(host)

                
    def remove(self, view_list):
        
        view_list = self.list_format(view_list)
        
        for host in view_list: self.pops(host) 
                  
            
    def pops(self, host):
        try:
            pos = self.batch_host_list.index(host.lower())
            self.batch_host_list.pop(pos)
            print 'removed', host.upper()
        except: print 'error %s was not removed' % host.upper()
        
        
    def make_ip_list(self):
        self.ip_list = []
        for host in self.batch_host_list:
            try: 
                key = self.dev_con.search_db[host.lower()]['key']
                ip = self.dev_con.dict_db[key]['ip']
                if ip not in self.ip_list: self.ip_list.append(ip)
            except type: print 'error %s ip address not found' % host
        
        
    def batch_ping(self): 
        self.make_ip_list()
        return self.mt_ping(self.ip_list)
    
    
    def batch_rlook(self): 
        self.make_ip_list()
        return self.mt_dns_rlook(self.ip_list)
    
    
    def batch_vty(self):
        """
        perfrom command(s) on multiple hosts
        screen data will be wrote to self.out_file
        """
        
        try: cmd = self.cli_con.cmd_list
        except: return 'Enter a command with cmd='
        print 'command(s) to run %s \n' % cmd
        
        if len(self.batch_host_list) == 0: print 'No hosts are specified, search on host(s) and then enter batch add'
        for host in self.batch_host_list:
            try: 
                key = self.dev_con.search_db[host.lower()]['key']
                ip = self.dev_con.dict_db[key]['ip']
                print 'connecting to %s with %s' % (host, ip)
                port = self.cli_con.test_session(host, ip)[1]
                time.sleep(self.time_wait)
                out = self.cli_con.vty_session(ip, host, port, cmd)
                
                if out: 
                    self.view(out)
                    self.list_to_file(out, self.out_file, 'a')
                
                time.sleep(self.time_wait)
                    
            except type: print 'error with host %s ip %s port % cmd %s' % (host, ip, port, cmd)
    
    
    def com(self, q, view_list):
        """
        \n Batch commands
        \n help         display this help information
        \n add          add new hosts to the batch list
        \n clear        delete the batch list
        \n remove       remove host entry(s) from batch list
        \n view ip      view ip address list
        \n view host    view host list
        \n ping         perform a multithreaded ping on ip_list
        \n rlook        perfrom a multithreaded reverse dns lookup on ip_list
        \n vty / tty    connect to vty on devices and run a command(s) and store screen output
        
        """
        if 'help' in q: return self.com.__doc__
        
        if 'add' in q: return self.insert(view_list)
        
        if 'clear' in q: self.clear()
        
        if 'remove' in q: self.remove(view_list)
        
        if 'view' in q:
            if 'ip' in q: 
                self.make_ip_list()
                self.view(self.ip_list)
            if 'host' in q: self.view(self.batch_host_list)
            
        if 'ping' in q: return self.batch_ping()
        
        if 'rlook' in q: return self.batch_rlook()
        
        if 'vty' in q or 'tty' in q: return self.batch_vty()
        
        
            

                
                
                
