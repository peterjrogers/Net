import telnetlib
from tools import Tools

try: import paramiko
except: pass

class Vty(Tools):
    def __init__(self, ip='192.168.1.18', name='pi', port=22):
        Tools.__init__(self)
       
        """
        VTY - Telnet and SSH
        Note SSH requires the pycrypto package which requires a C++ compiler for Windows.
        Microsoft Visual C++ can be downloaded for free and used for this.
        
        (c) 2012, 2013 Intelligent Planet Ltd
        """
        
        self.ip = ip
        self.name = name
        self.port = port
               
        self.telnet_timeout = 2
        self.telnet_cmd_timeout = 5
        self.telnet_sleep = 0.1
        
        self.verbose = 1
       
        self.ssh_key_file = 'c:/python27/ssh_host_keys'
        self.auth_pi()
        
    
    ##### TTY Auth #####
        
    def auth_pi(self):
        self.username = 'pi'
        self.password = 'raspberry'
       
    ##### Telnet Client #####
    
    def telnet_init(self, ip='', port=''):
        if not ip: ip = self.ip
        if not port: port = self.port
        
        try: self.telcon = telnetlib.Telnet(ip, port, self.telnet_cmd_timeout)
        except socket.error, e:
            if self.debug > 0: return (self.error, 'telnet_init', e)
           
           
    def telnet_login(self, user='', passw=''):
        if not user: user = self.username
        if not passw: passw = self.password
        
        self.telnet_read_until(self.telnet_login_text, user, 0)    #login
        self.telnet_read_until(self.telnet_pass_text, passw)    #password
        
        res = self.telcon.expect(self.telnet_banner_list, self.telnet_cmd_timeout)
        self.res = res[2].split('\r\n')[-1]    #banner
        
    
    def telnet_read_until(self, match, cmd, hide=1):
        res = self.telcon.read_until(match, self.telnet_timeout)
        self.telcon.write(cmd + '\r\n')
        if self.verbose > 0: 
            if hide == 1: print res, '*' * len(cmd)
            else: print res,
       
       
    def telnet_cmd(self, cmd):
        out = self.res
        self.telcon.write(cmd + '\r\n')
        res = self.telcon.expect(self.telnet_banner_list, self.telnet_cmd_timeout)
        out += res[2]
        while res[0] == 1:    #matched on '--More--'
            self.telcon.write(' ')
            out += '\r\n'
            res = self.telcon.expect(self.telnet_banner_list, self.telnet_cmd_timeout)
            out += res[2]
       
        #if self.verbose > 0: print out
        return out
           
       
    def telnet_exit(self):
        self.telcon.write(self.telnet_exit_text + '\r\n')
        self.telcon.close()
        
    
    def telnet_cisco(self):
        self.telnet_login_text = 'Username: '
        self.telnet_pass_text = 'Password: '
        self.telnet_exit_text = 'q'
        self.telnet_banner_list = ['\d+>', '--More--', '\d+#']
    
         
    def telnet_go(self, cmd_list='sh snmp loc', ip='', port=''):
        try:
            if 'str' in str(type(cmd_list)): cmd_list = [cmd_list]    #convert single command str to list
            self.out = []
            
            self.telnet_init(ip='', port='')
            self.telnet_login()
       
            for item in cmd_list:
                res = self.telnet_cmd(item.lstrip())
                self.out.append(res)
           
            self.telnet_exit()
       
            if self.out:
                self.telnet_out = [x.split('\r\n') for x in self.out]
                
        except: return 'Failed to connect'
           
           
    ##### SSH Client #####
   
    def ssh_init(self, ip='', port='', user='', passw=''):
        if not ip: ip = self.ip
        if not port: port = self.port
        if not user: user = self.username
        if not passw: passw = self.password
        
        if self.verbose > 2: print ip, port, user, passw
        
        self.ssh_key_load()
        self.ssh_banner = self.name + '#'
       
        self.sshcon = paramiko.SSHClient()
        self.sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshcon.connect(ip, port, user, passw)
       
       
    def ssh_cmd(self, cmd):
        stdin, stdout, stderr = self.sshcon.exec_command(cmd)
        return stdout.readlines()
       
       
    def ssh_exit(self):
        self.sshcon.close()
       
       
    def ssh_key_load(self):
        self.ssh_keys = paramiko.HostKeys()
        try: self.ssh_keys.load(self.ssh_key_file)
        except IOError, e:
            if 'No such file' in str(e): self.ssh_keys.save(self.ssh_key_file)
       
       
    def ssh_go(self, cmd_list='sh log'):
        try:
            if 'str' in str(type(cmd_list)): cmd_list = [cmd_list]    #convert single command str to list
            self.ssh_out = []
            self.ssh_init()
       
            for item in cmd_list:
                #self.ssh_init()
                res = self.ssh_cmd(item)
                self.ssh_out.append(self.ssh_banner + item) 
                for item in res: self.ssh_out.append(item)
                
            if self.verbose > 0: self.view(self.ssh_out)
            self.ssh_exit()

        except: return 'failed to connect'
        
        
    
