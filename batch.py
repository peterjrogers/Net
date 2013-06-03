from tools import Tools
from mnet3 import Mnet
import session

class Batch(Tools, Mnet):
    def __init__(self, dev_con=''):
        Tools.__init__(self)
        Mnet.__init__(self)
        
        """
        Batch processing tools
        Pass device class into this class as dev_con
        if dev_con is null then load device class here
        
        (c) 2012, 2013 Intelligent Planet Ltd
        """
        
        self.clear()
        
        if not dev_con:
            import device
            self.dev_con = device.Device()
        else: self.dev_con = dev_con    #passed into class
        
        self.ses_con = session.Launch()
    
    
    def clear(self): 
        self.host_list = []
        self.ip_list = []
        self.all_list = []
    
    
    def insert_batch(self, view_list):
        """
        read view_list and resolve entries to hostname and ip 
        and return a host list and ip list
        will only add entries if they do not already exist in the host list
        """
        try: view_list.sort()
        except: view_list = [view_list]
        
        for host in view_list:
            if host not in self.host_list:
                try: ip = self.dev_con.find_ip(host)
                except: ip = '0.0.0.0'
                self.host_list.append(host)
                self.ip_list.append(ip)
                res = host, ip
                self.all_list.append(res)
                
                
    def remove_batch(self, clist):
        """
        read clist and remove matching entries from batch list
        single entries can be input as string        
        """
        try: clist.sort()
        except: clist = [clist]
        
        for host in clist:
            try: 
                pos = self.host_list.index(host.lower())
                self.host_list.pop(pos)
                self.ip_list.pop(pos)
                self.all_list.pop(pos)
                print 'removed', host.upper()
            
            except: print 'error %s was not removed' % host.upper()
        
    
    def view_all(self):
        for item in self.all_list: print item[0].upper(), '    ', item[1]
        
        
    def view(self, clist):    #custom version of view
        for item in clist:
            print item.upper()
        
        
    def batch_ping(self): return self.mt_ping(self.ip_list)
    
    
    def batch_rlook(self): return self.mt_dns_rlook(self.ip_list)
    
    
    def batch_vty(self, cmd_list):
        """
        perfrom command(s) on multiple hosts
        screen data will be returned as a dict
        out[host] = cmd_output
        """
        out = {}
         
        print 'command(s) to run %s \n' % cmd_list
        
        for host in self.host_list:
            self.ses_con.ip = self.dev_con.find_ip(host)
            self.ses_con.host = host.upper()
            print 'connecting to %s at %s' % (host, self.ses_con.ip)
            res = self.ses_con.test_session()
            if res != 'fail': 
                raw = self.ses_con.py_session(cmd_list)
                if not raw: raw = 'error no output'
                out[host] = raw

    
    
    def com(self, q, view_list=[]):
        """
        \n Batch commands
        \n help         display this help information
        \n search       search the device list
        \n add          add new hosts to the batch list
        \n clear        delete the batch list
        \n remove       remove host entry(s) from batch list
        \n view ip      view ip address list
        \n view host    view host list
        \n view all     view ip and host combined
        \n ping         perform a multithreaded ping on ip_list
        \n rlook        perfrom a multithreaded reverse dns lookup on ip_list
        \n vty / tty    connect to vty on devices and run a command(s) and store screen output
        
        """
        if 'help' in q: print self.com.__doc__
        
        if 'search' in q: return self.dev_con.search_func(q[7:])
        
        if 'add' in q: return self.insert_batch(view_list)
        
        if 'clear' in q: self.clear()
        
        if 'remove' in q: self.remove_batch(view_list)
        
        if 'view' in q:
            if 'ip' in q: self.view(self.ip_list)
            if 'host' in q: self.view(self.host_list)
            if 'all' in q: self.view_all()
            
        if 'ping' in q: return self.batch_ping()
        
        if 'rlook' in q: return self.batch_rlook()
        
        if 'vty' in q or 'tty' in q: return self.batch_vty(view_list)
        
        
            

                
                
                
