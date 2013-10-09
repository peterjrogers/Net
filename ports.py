from tools import Tools

class Ports(Tools):
    def __init__(self, verbose=0):
        Tools.__init__(self)
        """
        Well known port search tool
        
        downloaded port list from
        http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv
        
        format of csv file
        Service Name,Port Number,Transport Protocol,Description,Assignee,Contact,Registration Date,Modification Date,Reference,Service Code,Known Unauthorized Uses,Assignment Notes
        ftp-data,20,tcp,File Transfer [Default Data],[Jon_Postel],[Jon_Postel],,,,,,
        ftp-data,20,udp,File Transfer [Default Data],[Jon_Postel],[Jon_Postel],,,,,,
        
        format of dictionary
        [portnum_protocol]['name'] = name
        [portnum_protocol]['description'] = description
        
         Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
        
        self.verbose = verbose
        self.port_dict = {}
        self.load_file = 'c:/ports.csv'
        self.load()
        
    def load(self):
        file = open(self.load_file, 'rU')
        for row in file:
            if row:
                try:
                    raw = row.split(',')
                    key = raw[1] + '_' + raw[2]
                    self.port_dict[key] = {}
                    self.port_dict[key]['name'] = raw[0]
                    self.port_dict[key]['description'] = raw[3]
                except: 
                    if self.verbose > 0: print 'error', row
                
                
    def find_port(self, port, protocol='tcp'):
        try: 
            key = str(port) + '_' + protocol.lower()
            name = self.port_dict[key]['name'].upper().rstrip()
            desc = self.port_dict[key]['description'].rstrip()
            return name, desc
        
        except: return port, protocol
                        
                            
