import sys, time, macs, device2, contact, mac, cache_flow, arps, ports2
import net2, os, mnet2, vty, session3, batch
from subprocess import Popen, PIPE
from tools import Tools

mac_con = macs.Macs()
dev_con = device2.Device()
contact_con = contact.Contact()
mac_oui = mac.Mac()
cache_con = cache_flow.Cache_flow()
ports_con = ports2.Ports()
mnet_con = mnet2.Mnet()
net_con = net2.Net()


class Cli(Tools):
    def __init__(self):
        Tools.__init__(self)
        
        """
        Search interface for host, ip  and extended information within device db
        Start point for Command line networking toolkit
        
        """
        
        self.verbose = 0
        
        ### cli vars ###
        self.search_txt = '\n\nsearch >>>'
        
        ### set the path to csv device files ###
        try: self.path = 'H:/crt/sessions/'
        except: self.path = 'C:/Program Files/SecureCRT/Sessions/'
        
        self.log_file = self.path + 'log'
        self.sticky = 1    #can be set to 0 to disable level1 cli
        self.session_fail_delay = 2
        self.total_records = len(dev_con.search_db)
        self.total_hosts = len(dev_con.index)
        self.batch_con = batch.Batch(dev_con, self)
        self.host_list = []
        self.arp_start()
        self.level_0()
        

    def level_0(self):
        """
        Top level function
        
        To exit from this level closes the cli app
        
        Search by host, ip, model, serial, mac, town, postcode etc
        
        ?            Display multiple matching host records\n
        @            Open a pre made session e.g. @ba\n
        %name,ip     Open ad-hoc session e.g. %Router1,10.1.1.1\n
        sticky 0     Disables level 1 CLI for cut & paste searches    sticky re-enables
        batch [help]    perform batch operations

        """
        print "%s records loaded for %s devices" % (self.total_records, self.total_hosts)
        
        out = []
        view_list = []
        
        while True:
            res = raw_input(self.search_txt)
            start = time.time()
            res = res.rstrip('\n').lower()
           
            if res:
            
                if res == 'exit': return    #exit the program
           
                if res == 'help':    #print the module docstring
                    print self.level_0.__doc__
                    print self.level_7.__doc__    #common tools
                    res = ''
               
                if res == '?':    #print each item in the view_list
                    try: 
                        for item in view_list: print item.upper()
                    except: pass
                    res = ''

                if '@' in res:    #open a previously made session file by file name
                    self.pre_session(res)
                    res = ''

                if '%' in res:    #open a new ad-hoc session - format is %hostname,ip_address
                    try:
                        raw = res[1:].split(',')
                        self.crt_session(raw[0], raw[1])
                    except: pass
                    res = ''
                    
                if 'sticky ' in res:    #disable level1 interface for copy / paste searches
                    if '0' in res: self.sticky = 0
                    else: self.sticky = 1
                    res = ''
                    
                if 'batch ' in res:    #perform batch operations - use batch help for extended help
                    batch_out = self.batch_con.com(res, self.host_list)
                    if batch_out: print batch_out
                    res = ''
                    
                res = self.level_7(res)    #check macthing commands in the common tools
                
                if res:    
                    """
                    If res did not match a command then perform a host search and return
                    a view_list if more than on host matches.
                    The view_list can then be used to specify batch host targets
                    """                    
                    view_list = self.host_search(res)
                    res = ''
                    
                
                    
    def level_1(self, hostname, ip_address):
        """
        Command line session function
        Perform actions on the selected device
        
        info          Display info records
        
        vty / tty     Open vty session to device
        http(s)       Open http ot https session to device
        
        %command      Run a single command on the device - e.g. %sh int desc
        cmd=a,b       Create a list of multiple commands to run - e.g. cmd=sh arp,sh int desc
        @cmd          Run multiple commands from list created with cmd=a,b
        
        ip=x.x.x.x    Change the session IP address
        +1 or -1       Increase / decrease the session IP adress by 1
        
        @arp           Command macro runs sh ip arp and then analyses output\n
        @x25           Command macro runs sh x25 route  sh x25 vc | inc Interface|Started|Connects\n
        @int           Command macro runs sh int desc  sh ip int brief  sh int count err  sh ip arp
                       sh ip bgp sum  sh ip route sum  sh ver | inc uptime|System|reason|cessor  
                       sh standby | inc Group|State|change|Priority\n
                       
        q              Exit session mode and return to search mode
        """
        
        c = 1
        while 1:
            print '\n%s >>>' % (hostname.upper()),
            q = raw_input()
            q = q.lower()
            
            if '@arp' in q: q = '%sh ip arp'
            
            if '@bip' in q: self.cmd_list = ['sh ip bgp sum | beg Neigh', 'sh controller vdsl 0/0/0 | inc dB|Speed|Reed|Err', 'sh controller vdsl 0/1/0 | inc dB|Speed|Reed|Err'] ; q = '@cmd'
            
            if '@mac' in q: q = '%sh mac-add dyn'
            
            if '@cache' in q: q = '%sh ip cache flow'
            
            if '@nex_mac' in q: q = '%sh mac address-table dynamic'
            
            if '@x25' in q: self.cmd_list = ['sh x25 rou','sh x25 vc | inc Interface|Started|Connects'] ; q = '@cmd'
            
            if '@int' in q: self.cmd_list = ['sh int desc','sh ip int brief','sh int count err','sh ip arp','sh ip bgp sum','sh ip route sum','sh ver | inc uptime|System|reason|cessor','sh standby | inc Group|State|change|Priority'] ; q = '@cmd'

            if 'ping' in q and len(q) == 4: q = 'ping %s' % ip_address ; c +=1

            if 'trace' in q: q = 'trace %s' % ip_address ; c +=1
            
            if 'scan' in q: q = 'scan %s' % ip_address ; c +=1
        
            if 'http' in q: self.start_http(q, ip_address) ; c +=1
            
            if 'info' in q: dev_con.show_info(hostname) ; c +=1
                
            if 'ip=' in q: ip_address = q[3:] ; c +=1
            
            if '+1' in q: 
                ip_address = self.ip_add(ip_address)
                print 'ip', ip_address ; c +=1
                
            if '-1' in q: 
                ip_address = self.ip_sub(ip_address)
                print 'ip', ip_address ; c +=1
            
            if 'help' in q: print self.level_1.__doc__ ; c +=1
                
            if '@cmd' in q:
                res = self.test_session(hostname, ip_address)
                if res[0] != 'fail': 
                    raw = self.py_session(ip_address, hostname, res[1], self.cmd_list)
                q = '' ; c +=1
            
            if 'vty' in q or 'tty' in q: self.crt_session(hostname, ip_address) ; c +=1
                
            if 'search' in q or 'q' in q or 'exit' in q: return
            
            if '@' in q: self.pre_session(q) ; c += 1
                        
            q = self.level_7(q)    #check matching commands in the common tools
            
            if '%' in q: 
                res = self.test_session(hostname, ip_address)
                if res[0] != 'fail': 
                    raw = self.py_session(ip_address, hostname, res[1], q[1:])
                q = '' ; c +=1
            
            c -= 1
            
            if c < 0: return
        
               

    def level_7(self, res):
        """
        arp [ip mac hostname]    Display arp records\n
        mac [mac]    Display mac records\n
        name        Display contact db records\n
        oui [mac]  Display MAC OUI info\n
        ports [# / name]  Display well known port info\n
        ping x.x.x.x [:port]  Ping IP / Port\n
        trace [ip]    Traceroute
        scan [ip]    Port scanner
        """
        
        if 'cmd=' in res: 
            self.cmd_list = res[4:].split(',')
            print self.cmd_list ; res = ''
        
        if 'arp ' in res:    #perform a search of the historic arp db
            self.arp_search(res[4:])
            res = ''
                
        if 'mac ' in res:    #perform a search of the historic mac db
            self.mac_search(res[4:])
            res = ''

        if 'name ' in res:    #perform a search of the contact db
            contact_con.search_func(res[5:])
            res = ''
            
        if 'oui ' in res:    #perform a OUI mac vendor lookup
            print mac_oui.id_mac(res[4:])
            res = ''
            
        if 'ports ' in res:    #perform a well know port lookup
            print ports_con.find_port(res[6:])
            res = ''
            
        if 'ping ' in res:    #perform a ping or port ping test by specifying the ip address and port if required
            self.ping_tool(res[5:])
            res = ''
            
        if 'trace ' in res:    #perform a traceroute
            out = mnet_con.mt_trace(res[5:])
            res = ''
            
        if 'scan ' in res:    #perfrom a port scan
            self.view(net_con.scan(res[5:]))
            res = ''
            
        return res    #returns the original string if no match
               
               
    def pre_session(self, res):    
        """
        Start pre made session from  self.path\Sessions\
        Use the launch function in session3.py with an empty connection_type
        Pass in the self.path value to keep it working with custom secure crt implementations
        """
        if len(res) > 1:
            ses_con = session3.SecureCRT(res[1:], '0.0.0.0', self.path)
            ses_con.launch()
            
            
    def crt_session(self, hostname, ip):
        """
        Make a session for SecureCRT and launch a new CRT window
        """
        ses_con = session3.SecureCRT(hostname, ip, self.path)
        ses_con.make()
        ses_con.launch()
        
        
    def test_session(self, hostname, ip):
        """
        Test the connection type and authentication
        """
        ses_con = session3.SecureCRT(hostname, ip, self.path)
        return ses_con.test(), ses_con.port
    

    def arp_start(self):
        self.arp_con = arps.Arp()
        
    def arp_search(self, res):
        """
        Search and display historical arp records and goto level_1 if a single matching entry is found
        """
        if res: 
            view_list = self.arp_con.search_mac(res)
            if len(view_list) == 1: 
                res = view_list[0].split('_')
                ip_address = res[0]
                hostname = res[1]
                print '\n Matched in ARP db  %s    %s\n' % (ip_address, hostname)
                self.arp_con.view_records(ip_address)
                self.level_1(hostname, ip_address)
            else:
                for item in view_list: print 'ARP db    ',item
        
        
    def mac_search(self, res):
        """
        Search and display historical mac records
        """
        if res: self.view(mac_con.search(res))
            
            
    def host_search(self, q):
        """
        Search and display host devices and goto level_1 if a single matching entry is found
        """
        if q:
            res = dev_con.search_func(q)
            self.host_list = dev_con.host_list
            if len(res) == 1 and self.sticky ==1:
                ip_address = dev_con.ip
                hostname = dev_con.host
                self.level_1(hostname, ip_address)
                
            else: return res    #return the list so it can be used for batch work
                
                
    def ping_tool(self, res):
        if res:
            if ':' in res:
                raw = res.split(':')
                ip_address = raw[0]
                port = raw[1]
                
            else: 
                ip_address = res
                port = ''
                
            con = net2.Net(ip_address, 'ping_test')
            
            if port:
                if ':80' in res: print con.test_http(80, ip_address)
                else: print con.test_port(int(port), ip_address)
                time.sleep(1)
                
            else: con.ping(ip_address)
            
            
    def start_http(self, protocol, url):
        ##### start "" "http://bbc.co.uk" #####
        cmd = 'start %s://%s' % (protocol, url)
        os.system(cmd)   
    
              
    def py_session(self, ip, host, port, cmd):
        out = self.vty_session(ip, host, port, cmd)
        return self.post_session(out, cmd)
    
    
    def vty_session(self, ip, host, port, cmd):
        print 'command(s) to run', cmd
        con = vty.Vty(ip, host, port)
        con.verbose = 0
        self.session_try = 1
        
        while self.session_try < 4:
        
            if port == 23:
                res = con.telnet_go(cmd)
                if res: self.session_fail()
                else: return con.telnet_out

            if port == 22:
                con.auth_produban()
                res = con.ssh_go(cmd)
                if res: self.session_fail()
                else: return con.ssh_out
                
        return ''

            
    def session_fail(self):
        print 'attempt %d failed' % self.session_try
        self.session_try += 1
        time.sleep(self.session_fail_delay)
            
        
    def post_session(self, out, cmd, silent=0):
        self.view(out)
        
        if out:
            if 'arp' in cmd: 
                try:
                    self.list_to_file(out, self.arp_con.cfile)
                    self.arp_start()
                    self.arp_con.arp_go()
                    if silent < 1: self.arp_con.save_report()
                except: pass
                
            if 'mac' in cmd: 
                self.list_to_file(out, mac_con.load_file)
                mac_con.load()
                mac_con.save()
                
            if 'cache' in cmd:
                self.list_to_file(out, cache_con.load_file)
                cache_con.test()
                
            if 'sh ip int brief' in cmd:
                self.list_to_file(out, self.log_file, 'a')
                
            else: self.list_to_file(out, self.log_file, 'a')
                
        return out
                  
       
def go():
    x = Cli()
    
    
if __name__ == "__main__":
    go()     
