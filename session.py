from subprocess import Popen

class SecureCRT():
    def __init__(self, connection_type, hostname, ip_address):   
        """
        This class is designed to create and use session files for Secure CRT 
        by cloning and modifying a pre made template session file.
        
        This class will add a new line (1) to a pre-made template file 
        by catenating self.ip_text and self.ip_address and saving the file 
        with hostname.ini in the relavent folder
        
        Template files must be prepared manually by making a session of each 
        connection type, including auto login credentials (if required)
        
        The process to create session template files and target directory's is as follows:
        1) Open secure crt and make a new session
        2) Go to folder C:\Program Files\SecureCRT\Sessions and open the session file in a text editor
        2) Create a blank first line in the file
        3) Remove the line containing S:"Hostname"=
        4) Save a template file for each connection type i.e. telnet.ini, ssh.ini, ssh2.ini
        5) Create output folders for each connection type in C:\Program Files\SecureCRT\Sessions
            i.e. C:\Program Files\SecureCRT\Sessions\telnet
                  C:\Program Files\SecureCRT\Sessions\ssh
                  C:\Program Files\SecureCRT\Sessions\ssh2
      
        Usage of the class:
        connection_type options are [telnet, ssh, ssh2]
        new connection types can be added by creating a folder and template file
        hostname is used to write the name of the session file
        ip_address is inserted into the session file and controls the connectivity
        
        session creation example:
        from python shell
        >>>import session
        >>>x = session.SecureCRT('ssh', 'my_router', '10.1.1.1')
        >>>x.make_session()
        
        session usage example:
        from windows command prompt
        c:\>securecrt /S "\ssh\my_router"
        
        from python shell
        >>>x.launch_session()
        
        Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
        
        #passed in class values
        self.connection_type = connection_type
        self.hostname = hostname
        self.ip_address = ip_address
        
        #file name and path values
        self.file_extension = '.ini'
        self.path = 'C:/Program Files/SecureCRT/Sessions/'
        self.output_path = self.path + self.connection_type + '/'
        self.output_file_name = self.output_path + self.hostname + self.file_extension
       
    
    def make_session(self):
        """
        A function designed to create the session text for a session.ini file
        and save the text into a new file in the following location:
        C:/Program Files/SecureCRT/Sessions/[connection type]/[hostname].ini
        i.e. C:/Program Files/SecureCRT/Sessions/ssh/my_router.ini
        """
        
        #read the session template
        self.session_template = open(self.path + self.connection_type + self.file_extension).read()
        
        #catanate the template and ip address
        self.ip_text = 'S:"Hostname"='
        self.output_text = self.ip_text + self.ip_address + self.session_template
        
        #write a new session file in the correct folder
        outfile = open(self.output_file_name, 'w')
        outfile.write(self.output_text)
        outfile.close()
        
        
    def launch_session(self):
        """
        A function designed to open the session file that 
        was previously created with self.make_session()
        
        Uses Popen to open the session via windows command line
        Caveat - Tested on Win32 platforms only
        
        manual example of the operation:
        Popen('securecrt /S "\ssh\my_router"')
        
        Note - the string creation is in two parts as issues seen 
        with multiple backslash chars and string substitution
        \\\ is escape and \\ which is needed for Popen
        this ends up as single \ when the string passed from
        Popen to win cmd
        """
        
        #build the command string and execute it
        part_a = 'securecrt /S "\\\%s' % (self.connection_type)
        part_b = '%s"' % (self.hostname)
        cmd = "Popen('%s\\\%s')" % (part_a, part_b)
        exec(cmd)   

