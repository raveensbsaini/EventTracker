import subprocess,shlex
import re
def find_event():
    with open("/proc/bus/input/devices","r") as file:
        file_data = file.read()
        file_data = file_data.split("\n\n")
        for row in file_data:
            print("-------------------------------------------------------")
            print(row)
            new = re.match("H:",row,re.DOTALL)
            print("new =======",new)
            if new != None:
                print(new[0])
                break
if __name__ == "__main__":
    find_event()
        
    
