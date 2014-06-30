import os, time

class Vty():
    def __init__(self, hostname, out_dict):
                
        self.banner_id = 'WARNING'    #string used to determine if a banner is present
        self.banner_end = 'prosecuted'    #string used to determine end of the banner
        
        self.delay = 0.5
        self.out_dict = out_dict
        self.hostname = hostname.lower()
        
        self.check_out_dict()
        self.more = '--More--'
        
        
    def check_out_dict(self):
        """ i) check if a dict is passed in, if not create a new dict
            ii) check if a key exists for the hostname in the dict
            iii) if not create a hostname key 
        """        
        if not self.out_dict: self.out_dict = {}
        try: self.out_dict[self.hostname]
        except: self.out_dict[self.hostname] = {}
        
        
    def format_out(self, line):
        """ skip empty lines & strip out leading and trailing spaces  """
        line = self.trim_more(line)
        line.lstrip().rstrip()
        if len(line) == 1 and ' ' in line: return
        if line: self.out.append(line)
        
        
    def trim_more(self, line):
        """ Strip out --More-- and \x08 from telnet output """
        try:
            pos = line.index(self.more)
            start = pos + 8
            out = ''
            for item in line[start:]:
                if ord(item) != 8: 
                    if item: out += item
            return out
            
        except: return line
        
        
    def trim_banner(self):
        """ remove the login banner from the output """
        self.out = []
        if self.banner_id in self.read_out:
            start =0
            for line in self.split_out:
                if self.banner_end in line: 
                    start =1
                    continue
                if start == 1:  self.format_out(line)
        else: 
            for line in self.split_out: self.format_out(line)
              
            
    def build_cmd_list(self, cmd_list):
        """ if cmd_list is a string enclose it in a list """
        if 'str' in str(type(cmd_list)): self.cmd_list = [cmd_list]
        else: self.cmd_list = cmd_list
        
        
    def execute_commands(self):
        """
        use with self.build_cmd_list(cmd_list)
        will accept single or multiple commands
        in a list format, i.e.
        cmd_list = ['sh ver', 'sh log']
        """
        
        for self.command in self.cmd_list:
            self.init_con()
            time.sleep(self.delay)
            if self.verbose > 0: print '\n\n', self.hostname + '#' + self.command, '\n\n'
            error = self.exec_cmd(self.command)
            if error: self.out = error
            else: 
                self.read()
                self.trim_banner()
                
            self.parse_fixed_width()
            time.sleep(self.delay)
            if self.verbose > 0: self.view(self.out)
            
    
    def count_rows(self, rows, splitter):
        """ count the rows and return a list of the row count """
        return [len(self.split_row(row, splitter)) for row in rows]
        
        
    def unique_list(self, num_list):
        """ filter an input list into unique values"""
        out = []
        for num in num_list:
            if num not in out: out.append(num)
        return out
        
        
    def mode_list(self, num_list):
        """ return the mode average of numbers in num_list """
        unique = self.unique_list(num_list)
        max = 0 ; number = 0
        for num in unique:
            res = num_list.count(num)
            if  res > max: max = res ; number = num
        return number, num_list.index(number)
                  
    
    def split_row(self, row, splitter='  '):
        try:
            out = []
            temp = row.split(splitter)
            for item in temp:
                if item: out.append(item)    #ignore blanks
            return out
        except: return 0
        
    
    def get_field_width(self):
        """
        discover the fixed field widths for table type views and produce a dict of values
        {0: {'Interface': {'start': 0, 'end': 26}}, 1: {'IP-Address': {'start': 27, 'end': 42}}, 2: {'OK?': {'start': 43, 'end':
        46}}, 3: {'Method': {'start': 47, 'end': 53}}, 4: {'Status': {'start': 54, 'end': 75}}, 5: {'Protocol': {'start': 76}}}
        """
        self.ignore_list = []
        out = {}
        splitter_list = ['  ', '\t', ' ']
        
        #try and find the best char to split the data into entries
        for splitter in splitter_list:
            nums = self.count_rows(self.out, splitter)
            if len(self.unique_list(nums)) == 1: break
        
        pos = self.mode_list(nums)[1]    #get the self.out index pos of the first row with the mode avergae num of entries
        
        row = self.out[pos]
        desc = self.split_row(row)
        if len(desc) < 2: return out    #ignore single field rows
        
        for item in self.ignore_list:
            if item in self.command.lower(): return out
        pos = 0
        
        for item in desc:
            start = row.index(item)
            out[pos] = {}
            out[pos][item] = {}
            out[pos][item]['start'] = start
            
            if pos > 0:
                out[pos-1][last_item]['end'] = start - 1    #set the previous item's end value
            
            last_item = item
            pos += 1
        print out                   
        return out
            
            
    def parse_fixed_width(self):
        """
        parse the table view using fixed length fields
        use the self.out data that is split into lines by newline
        """
        res = self.get_field_width()    #get the field start / end values
        
        if not res:    
            #save the output in 1 record as parsing not possible
            self.out_dict[self.hostname.lower()][self.command.lower()] = self.out
            return
        
        #build the dict for parsed output
        self.out_dict[self.hostname.lower()][self.command.lower()] = {}
        
        row_pos = 0
        for row in self.out:
            if row_pos == 0: 
                row_pos += 1
                continue    #skip the first row
                
            for key in res.keys():
                item = res[key].keys()[0]
                start = res[key][item]['start']
                    
                try:
                    end = res[key][item]['end']
                    value = row[start:end].lstrip().rstrip()
                except: value = row[start:].lstrip().rstrip()
                
                if key == 0:
                    #make a sub entry for the first entity - i.e. the interface name
                    try:     #check if the sub_key is unique
                        if self.out_dict[self.hostname.lower()][self.command.lower()][value]: pass
                        sub_key = value + '_' + str(row_pos)
                    except: sub_key = value
                    
                    self.out_dict[self.hostname.lower()][self.command.lower()][sub_key] = {}
                    print 'new sub key', value
                
                else:
                    #add the entry to the entity - i.e. protocol down
                    try: self.out_dict[self.hostname.lower()][self.command.lower()][sub_key][item] = value
                    except: print 'error with key', sub_key, item
                         
                print '>>>', item, value
            
            row_pos += 1
            
           
    def do_cmd(self, cmd_list='sh ver'):
        """
        example of how to use
        """
        self.check_auth()
        self.init_con()
        self.build_cmd_list(cmd_list)
        self.execute_commands()
        self.close()
        
