import subprocess,shlex
import re   
def find_event():
    return_list = []
    with open("/proc/bus/input/devices","r") as file:
        file_data = file.read()
        file_data = file_data.split("\n\n")
        EV_SYN= None #(0x00): Synchronization events
        EV_KEY= None #(0x01): Keyboard/Button events
        EV_REL= None #(0x02): Relative axis events (like mouse movement)
        EV_ABS= None #(0x03): Absolute axis events (like touchscreen)
        EV_MSC= None #(0x04): Miscellaneous events
        EV_LED= None #(0x11): LED events
        EV_SND= None #(0x12): Sound events
        mouse = None
        for row in file_data:
            match_kbd = re.search("Handlers=.*?kbd.*",row)
            match_Handlers = re.search("Handlers=.*",row)
            if match_Handlers == None:
                continue
            match_mouse = re.search("Handlers=.*?mouse.*",row)
            match_ev = re.search("EV=(.*)",row)
            match_name = re.search('N: Name=(.*)',row)           
            match_eventx = re.search("event(\d+)",match_Handlers[0])
            eventx = int(match_eventx[1])
            if match_ev != None:
                match_ev =int(match_ev[1],16)
                match_ev = bin(match_ev)[2:].zfill(16)             
                if match_ev[-1] == "1":
                    EV_SYN=True 
                if match_ev[-2] == "1":
                    EV_KEY = True
                if match_ev[-3] == "1":
                    EV_REL= True
                if match_ev[-4] == "1":
                    EV_ABS = True
                if match_ev[-5] == "1":
                    EV_MSC = True
                if match_ev[-6] == "1":
                    EV_LED = True
                if match_ev[-7] == "1":
                    EV_SND = True          
        
            if match_kbd != None and  EV_KEY == True:
                return_list.append((match_name[1][1:-1],eventx))
            elif match_mouse != None and EV_REL == True:
                return_list.append((match_name[1][1:-1],eventx))
    # print(return_list)
    return return_list
if __name__ == "__main__":
    find_event()
    
