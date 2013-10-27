from device_super_dict import Super_dict
import net2, session3, hosts

hosts_con = hosts.Hosts()

class Device(Super_dict):
    def __init__(self):
        Super_dict.__init__(self)
       
        """
        Device db
       
        self.dict_db format is [hostname][ip  |  user specified fields]
        """
       
        self.path = 'H:/crt/sessions/'
       
        self.load_file = self.path + 'Devices.csv'
        self.bt_load_file = self.path + 'bt_Devices.csv'
        self.bt_update_file = self.path+ 'bt_device_updates.csv'
       
        self.dict_file = 'c:/device_db'
        
        self.device_load()
        self.load_hosts()
       
       
    def device_load(self):
        self.load_csv(self.load_file)
        self.load_csv(self.bt_load_file)
        self.load_csv(self.bt_update_file)
        
        
    def load_hosts(self):
        """
        get_hosts returns a tuple of hostsname, ip_address, description
        """
        try: 
            head = ['host', 'ip', 'desc']
            gen = hosts_con.get_hosts()
            while 1: 
                res = gen.next()
                if res[0] not in self.index:
                    self.add_record(head, res)
        except: pass

        
    def search(self):    #search the device db and return host and ip for single matching entry
        while True:
            q = raw_input('Search >>>')
            q = q.rstrip('\n').lower()
            
            if q: 
                res = self.search_func(q)
                
                if len(res) ==1:
                    self.display(res[0])
                
                
    def search_func(self, q):
        if q in self.index: res = [q]
        else:
            res = self.search_hash(q)
        
        for item in res: self.display_host_search(item)
        print '\n', len(res), 'Result(s)\n'
        return res
        
        
    def show_info(self, host): self.view(self.display(host))
        
        
    def display_host_search(self, txt):
        try:
            res = self.hash_index(txt)
            self.host = self.dict_db[res[0]]['host'].upper()
            self.ip = self.dict_db[res[0]]['ip']
            print '%s%s %s%s %s' % (self.host, self.space(self.host, 40), self.ip, self.space(self.ip, 18), txt.upper())
        except: pass
                   
                         
