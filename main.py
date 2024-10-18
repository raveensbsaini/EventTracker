import struct
while True:
    x = input("enter string: ")
    print(struct.calcsize(x))

    
filepath = "/dev/input/event4"
bytes_size = struct.calcsize(l)
print(bytes_size)
