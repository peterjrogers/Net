from tools import Tools
import pickle

class Super_dict(Tools):
    def __init__(self):
        Tools.__init__(self)
       
        """
        Dictionary storage method
        Use # followed by csv fields to define headers e.g. #host, ip, model, serial number
        
        dictionary format example
        dict_db[unique numeric key] = {}
        dict_db[unique numeric key]['host'] = 'router-01'
        dict_db[unique numeric key]['ip'] = '1.1.1.1'
        dict_db[unique numeric key]['model'] = 'cisco 2811'
        
        dictionary search index
        search_db['router-01'] = {}
        search_db['router-01']['tag'] = 'host'
        search_db['router-01']['key'] = unique numeric key
        search_db['1.1.1.1'] = {}
        search_db['router-01']['tag'] = 'ip'
        search_db['router-01']['key'] = unique numeric key
        
        host entries appended to the self index list to provide a way to check for unique entries when adding data
        data entries appended to the register if unique, if not the key number is added to the entry i.e. Cisco    #123
        
        Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
       
        self.verbose = 1
        self.space_size = 18
        self.index = []
        self.register = {}
        self.dict_db = {}
        self.search_db = {}
        
           
    def load_csv(self, cfile):
        file = open(cfile, 'rU')
        for row in file:
            if row:
                if '#' in row[0]: head = row[1:].strip('\n').lower().split(',')    #['#Host', 'IP', 'MAC', 'Serial', 'Model', 'Location\n']
                else:
                    res = row.strip('\n').strip('"').rstrip(' ').lower().split(',')
                    self.add_record(head, res)
                        
                     
    def add_record(self, head, row):
        try:
            if row[0] in self.index:
                key = str(self.hash_index(row[0])[0])
            else:
                key = str(len(self.dict_db) + 1)
                self.dict_db[key] = {}
                self.index.append(row[0])
        except: return row, 'fail'
               
        pos = 0
        for item in row:
            if row[pos]:
                try:
                    value = row[pos]
                    self.dict_db[key][head[pos]] = value
                                    
                    if pos > 0:
                        try: 
                           ignore = self.register[value]
                           value = '%s    #%s' % (value, key)
                        
                        except: self.register[value] = ''
                        
                    self.search_db[value] = {}
                    self.search_db[value]['tag'] = head[pos]
                    self.search_db[value]['key'] = key
                    
                except: print 'failed', value, row[0], pos, len(row), len(head)
            pos += 1
                                         
                       
    def search_hash(self, txt): return [x for x in self.search_db.keys() if txt in x]
    
    
    def hash_index(self, txt):
        try:
            res = self.search_db[txt] 
            return res['key'], res['tag']
        except: return ''
        

    def list_view(self, clist):    #retreive the key for full record
        out = []
        
        try: clist.sort()
        except: clist = [clist]
        
        for entry in clist:
            res = self.hash_index(entry)[0]
            out.append(res)
        return out
       
       
    def search_list(self, txt):    #return matching keys
        return self.list_view(self.search_hash(txt))
        
        
    def display(self, txt, filter_list=''):    #display records
        res = self.search_list(txt.lower())
        for item in res:
            print '\n', str(item).upper()
            self.view(self.display_view(item))
       
       
    def display_view(self, txt):    #format record for display
        out = []
        res = self.dict_db[txt]
        key_list = res.keys()
        for key in key_list:
            res_out = '%s%s %s%s' % (key.capitalize(), self.space(key, self.space_size), res[key].upper(), self.space(res[key], self.space_size))
            out.append(res_out)
        return out
        
