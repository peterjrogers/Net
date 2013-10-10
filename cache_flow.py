from tools import Tools
import ports

ports_con = ports.Ports()

class Cache_flow(Tools):
    def __init__(self, verbose=0):
        Tools.__init__(self)
        """
        Cisco IP Cache Flow parse tool and Db viewer
        
        SrcIf         SrcIPaddress       DstIf             DstIPaddress    Pr SrcP DstP    Pkts
        Fa0/1         10.155.20.122   Se0/0:0.101*  10.7.10.124     01 0000 0000   219 
        Fa0/1         10.155.20.123   Se0/0:0.101*  10.7.10.124     01 0000 0000   219 
        Fa0/0         10.182.137.8    Se0/0:0.101*  62.239.26.81    06 C508 07D0     2  
        
        [flow_id] = {}
        [flow_id][SrcIPaddress]
        [flow_id][DstIPaddress]
        [flow_id][SrcIf]
        [flow_id][DstIf]
        [flow_id][Protocol]
        [flow_id][SrcPort]
        [flow_id][DstPort]
        [flow_id][Packets]
        
        Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
        
        self.limit = 200
        self.verbose = verbose
        self.cache_dict = {}
        self.protocol_dict = {1:'ICMP',2:'IGMP',4:'IP',6:'TCP',8:'EGP',9:'IGP',17:'UDP',50:'ESP', 88:'IGRP',89:'OSPF',94:'IPIP'}
        self.display_heading = '\nSrcIPaddress       SrcPort          DstIPaddress       DstPort        Protocol    Packets\n'
        
        
                
    def test(self):
        file = open('c:/R++', 'rU')
        self.cache_dict = {}
        self.load(file)
        #self.out = self.display()
        #self.view(self.out)
        res = self.top_talk()
        out = self.display(res)
        self.view(out)
        
        
    def load(self, res):
        start = 0
        for row in res:
            if row:
                if 'SrcIf' in row: start +=1
                if self.verbose > 0: print row
                
                if start > 0 and '.' in row:
                    try:
                        flow_id = str(len(self.cache_dict) + 1)
                        raw = row.split()
                        protocol = self.protocol_search(int(raw[4], base=16))
                        src_port = int(raw[5], base=16)
                        dst_port = int(raw[6], base=16)
                        self.cache_dict[flow_id] = {}
                        self.cache_dict[flow_id]['SrcIPaddress'] = raw[1]
                        self.cache_dict[flow_id]['DstIPaddress'] = raw[3]
                        self.cache_dict[flow_id]['SrcIf'] = raw[0]
                        self.cache_dict[flow_id]['DstIf'] = raw[2]
                        self.cache_dict[flow_id]['Protocol'] = protocol
                        self.cache_dict[flow_id]['SrcPort'] = ports_con.find_port(src_port, protocol)[0]
                        self.cache_dict[flow_id]['DstPort'] = ports_con.find_port(dst_port, protocol)[0]
                        self.cache_dict[flow_id]['Packets'] = raw[7]
                    except: 
                        if self.verbose > 0: print row
                    
                    
    def protocol_search(self, protocol):
        try: return self.protocol_dict[protocol]
        except: return protocol
        
                    
    def view_dict(self, filter=''): self.view_pretty(self.cache_dict, filter)    #filter based on exact match or like match within key
                    
                    
    def search_dict(self, txt):    
        """
        search all record fields and return a list of 
        matching keys for viewing with display
        """
        out = []
        key_list = self.cache_dict.keys()
        for key in key_list:
            for item in self.cache_dict[key]: 
                res = str(self.cache_dict[key][item])
                if txt in res: 
                    if key not in out: out.append(key)
        return out
        
        
    def search(self, txt): 
        key_list = self.search_dict(txt.upper())
        if len(key_list) > 0: 
            res = self.top_talk(key_list)
            self.view(self.display(res))
        
        
    def top_talk(self, key_list=''):
        """
        sort the top n of flows according to number of packets
        """
        out = [1]
        if not key_list: key_list = self.cache_dict.keys()
        for key in key_list:
            res = int(self.cache_dict[key]['Packets'])
            if res > min(out):
                out.append(res)
                out.sort()
                if len(out) > self.limit:
                    out.pop(0)
        
        key_out = []            
        for item in out:
            for key in key_list:
                if int(self.cache_dict[key]['Packets']) == item: key_out.insert(0, key)
                
        return key_out
                
                    
                
    def display(self, key_list=''):    #format records for display
        out = [self.display_heading]
        if not key_list: key_list = self.cache_dict.keys()
        for key in key_list:
            dst_ip = self.cache_dict[key]['DstIPaddress']
            src_ip = self.cache_dict[key]['SrcIPaddress']
            dst_port = self.cache_dict[key]['DstPort']
            src_port = self.cache_dict[key]['SrcPort']
            protocol = self.cache_dict[key]['Protocol']
            packets = self.cache_dict[key]['Packets']
            res_out = '%s%s  %s%s  %s%s  %s%s  %s%s  %s' % (src_ip, self.space(src_ip, 17), src_port, self.space(src_port, 15), dst_ip, self.space(dst_ip, 17), dst_port, self.space(dst_port, 15), protocol, self.space(protocol, 10), packets)
            out.append(res_out)
        return out

          

        

        
        
