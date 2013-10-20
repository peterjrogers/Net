from tools import Tools

class X25(Tools):
    def __init__(self, verbose=0):
        Tools.__init__(self)
        """
        X.25 Routing parser for cisco routers
        
        
        format of router output
        r01#sh x25 rou | inc dest|0/0
        1  dest ^(0000111111).*                              xot 10.11.12.13 
        2  dest ^(0000111112).*                              xot 10.11.12.14 
        
        format of dictionary
        key = auto incrementing integer
        [key]['router'] = hostname
        [key]['route_id'] = route_num
        [key]['x25_route'] = destination
        [key]['ip_address'] = ip_add
        [key]['match'] = match
        
        Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
        
        self.verbose = verbose
        self.x25_dict = {}
        self.route_list = []
        self.load_file = 'c:/x25'
        self.out_file = 'c:/x25_out'
        self.display_heading = '\n  #           X.25 route                IPaddress       match       router    \n'
        self.load()
        
        
    def load(self):
        file = open(self.load_file, 'rU')
        for row in file:
            if row:
                try:
                    #print row
                    if '#sh' in row: 
                        hostname = row.split('#')[0]
                    else:
                        raw = row.split()
                        if len(raw) == 1 and '/' in row: 
                            self.x25_dict[key]['match'] = raw[0]
                            continue
                        
                        if len(raw) == 5:
                            key = len(self.x25_dict) + 1
                            self.x25_dict[key] = {}
                            self.x25_dict[key]['router'] = hostname
                            self.x25_dict[key]['route_id'] = raw[0]
                            self.x25_dict[key]['x25_route'] = raw[2]
                            self.x25_dict[key]['ip_address'] = raw[4]
                            self.x25_dict[key]['match'] = 'true'
                            
                            if raw[2] not in self.route_list: self.route_list.append(raw[2])
                            #print key, hostname, raw[0], raw[2], raw[4]
                        
                except: 
                    try: 
                        print 'error with', row
                        del self.x25_dict[key]
                    except: pass
                    
    
    def view_dict(self, filter=''): self.view_pretty(self.x25_dict, filter)    #filter based on exact match or like match within key
    
    
    def test(self, search='true'):
        res = self.search_dict(search)
        print self.display_heading
        self.view(self.display(res))
    
    
    def search_dict(self, txt):    
        """
        search all record fields and return a list of 
        matching keys for viewing with display
        """
        out = []
        key_list = self.x25_dict.keys()
        for key in key_list:
            for item in self.x25_dict[key]: 
                res = str(self.x25_dict[key][item])
                if txt in res: 
                    if key not in out: out.append(key)
        return out
        
        
    def search_routes(self):
        out = []
        self.route_list.sort()
        key_list = self.x25_dict.keys()
        for item in self.route_list:
            for key in key_list:
                x25_route = self.x25_dict[key]['x25_route']
                if item == x25_route: out.append(key)
        return out
       
    
    def report_routes(self):
        res = self.search_routes()
        out = self.display(res)
        self.list_to_file(out, self.out_file)            
    
    
    def display(self, key_list=''):    #format records for display
        out = []
        if not key_list: key_list = self.x25_dict.keys()
        for key in key_list:
            router = self.x25_dict[key]['router']
            route_id = self.x25_dict[key]['route_id']
            x25_route = self.x25_dict[key]['x25_route']
            ip_address = self.x25_dict[key]['ip_address']
            match = self.x25_dict[key]['match']
            res_out = ' %s%s dest %s%s  %s%s  %s%s  %s' % (route_id, self.space(route_id, 7), x25_route, self.space(x25_route, 22), ip_address, self.space(ip_address, 17), match, self.space(match, 7), router)
            out.append(res_out)
        return out
                    
                    
                    
