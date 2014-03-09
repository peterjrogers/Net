import paramiko, os, time
from tools import Tools

class Ssh(Tools):
    def __init__(self, ip, hostname, auth_con=''):
        Tools.__init__(self)
        
        """
        usage - 
        con = ssh.Ssh(ip, host, auth_con)
        """
       
        self.ip = ip
        self.hostname = hostname
        self.port = 22
        self.verbose = 1
        self.user = ''
        self.password = ''
        self.auth_con = auth_con
        self.path = os.getcwd() + '\\'
        self.debug_file = self.path + self.hostname + '_ssh_debug.log'

        self.banner_id = 'WARNING'    #string used to determine if a banner is present
        self.banner_end = 'prosecuted'    #string used to determine end of the banner
        self.delay = 0.5
        
        #option is provided to pass in a dict for
        #the storage of all command output
        try: self.out_dict[self.hostname.lower()]
        except: 
            self.out_dict = {}
            self.out_dict[self.hostname.lower()] = {}
        
        
    def start_debug(self):
        """
        start a paramiko debug log file for this session
        """
        paramiko.util.log_to_file(self.debug_file)
        
        
    def view_debug(self):
        """
        view a paramiko debug log file for this session
        """
        print open(self.debug_file).read()
        
        
    def check_auth_con(self):
        """
        If auth_con is not passed in then 
        start an auth instance for this session
        """
        if not self.auth_con:
            import auth
            self.auth_con = auth.Auth()
            self.auth_con.auth_tacacs()
                
                
    def check_auth(self):
        """
        if self.user / self.password are blank then 
        get user / password via auth module
        """
        if not self.user:
            self.check_auth_con()
            self.user = self.auth_con.tacacs_user
                
        if not self.password:
            self.check_auth_con()
            self.password = self.auth_con.tacacs_password  
    
    
    def init_con(self):
        try:
            self.con = paramiko.SSHClient()
            self.con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.con.connect(self.ip, self.port, self.user, self.password)
        except BaseException, e: return e
        
        
    def init_cmd(self, command):
        try: self.stdin, self.stdout, self.stderr = self.con.exec_command(command)
        except BaseException, e: return e
        
            
    def write(self, command): 
        try: self.stdin.write(command)
        except BaseException, e: return e
       
        
    def flush(self): 
        try: self.stdin.flush()
        except BaseException, e: return e
        

    def format_out(self, line):
        """
        strip out leading and trailing space
        skip empty lines
        """
        line.lstrip().rstrip()
        if len(line) == 1 and ' ' in line: return
        if line: self.out.append(line)
        
    
    def trim_banner(self):
        """
        remove the login banner from the output
        """
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
            
            
    def read(self): 
        try: 
            self.read_out = self.stdout.read()
            self.split_out = self.read_out.split('\r\n')    #convert from string to list
            self.trim_banner()
        except BaseException, e: return e
             
        
    def close(self): 
        try: self.con.close()
        except BaseException, e: return e
    
    
    def build_cmd_list(self, cmd_list):
        """
        if a single command is passed in via
        a string then enclose it in a list
        """
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
            error = self.init_cmd(self.command)
            if error: self.out = error
            else: self.read()
                
            self.parse_fixed_width()
            time.sleep(self.delay)
            if self.verbose > 0: self.view(self.out)
            
    
    def count_rows(self, rows, splitter):
        """ count the rows and return a list of the row count """
        return [len(self.split_row(row, splitter)) for row in rows]
        
        
    def unique_list(self, nums):
        """ filter an input list into unique values"""
        out = []
        for num in nums:
            if num not in out: out.append(num)
        return out
        
        
    def mode_list(self, nums):
        """ return the mode average of a list """
        unique = self.unique_list(nums)
        max = 0 ; number = 0
        for num in unique:
            if  nums.count(num) > max: max = nums.count(num) ; number = num
        return number, nums.index(number)
                  
    
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
        
        # calculate the mode average column width for a given splitter char
        # and use the first row of that length as the header fields
        for splitter in splitter_list:
            nums = self.count_rows(self.out, splitter)
            if len(self.unique_list(nums)) == 1: break
        
        pos = self.mode_list(nums)[1]
        
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
        
      
    def test(self, cmd='sh ver'):
        self.check_auth()
        self.init_con()
        self.init_cmd(cmd)
        self.read()
        self.view(self.out)
        self.close()

     
        
