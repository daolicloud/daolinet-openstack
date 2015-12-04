import genl

data = "\x40\x40\x40\x00"
size = 4

sock, fid = genl.create()
print "Sent %s" % genl.send(sock, fid, data, size)
num, data = genl.recv(sock, fid)
print "Recv %s:%s:%s" % (num, len(data), data)
for i in data:
    print "%X" % ord(i)
genl.close(sock)

