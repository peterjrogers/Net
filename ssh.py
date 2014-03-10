import paramiko, os
from tools import Tools

class Ssh(Tools):
    def __init__(self, ip, hostname, out_dict='', auth_con=''):
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
        
        self.newline = '\r\n'
        self.delay = 0.5
        
        
    def start_debug(self):
        """ start a paramiko debug log file for this session """
        paramiko.util.log_to_file(self.debug_file)
        
        
    def view_debug(self):
        """ view a paramiko debug log file for this session """
        print open(self.debug_file).read()
        
        
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
        
            
    def read(self): 
        try: 
            self.read_out = self.stdout.read()
            self.split_out = self.read_out.split(self.newline)    #convert from string to list
        except BaseException, e: return e
             
        
    def close(self): 
        try: self.con.close()
        except BaseException, e: return e
        
        
    def check_auth_con(self):
        """ If auth_con is not passed in then start a new auth instance for this session """
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
    
    
