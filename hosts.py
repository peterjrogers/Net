class Hosts():
    def __init__(self, verbose=0):
        """
        Generator function to iterate the windows host file
        """

        self.verbose = verbose
        self.load_file = 'C:/WINDOWS/system32/drivers/etc/hosts'
        
    
    def get_hosts(self):
        file = open(self.load_file, 'rU')
        for row in file:
            if row:
                if '#' not in row[0]:
                    raw = row.lstrip().rsplit()
                    try:    
                        self.ip = raw[0]
                        self.host = raw[1].lower()
                        
                        res = row.find('#')
                        if res != -1: self.desc = row[res:].rstrip()
                        else: self.desc = ''
                        
                        yield self.host, self.ip, self.desc
                            
                    except: pass
