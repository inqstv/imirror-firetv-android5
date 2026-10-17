import struct,sys
def patch(path):
    d=bytearray(open(path,'rb').read())
    shoff,=struct.unpack_from('<I',d,32); shentsize,shnum,shstrndx=struct.unpack_from('<HHH',d,46)
    secs=[struct.unpack_from('<IIIIIIIIII',d,shoff+i*shentsize) for i in range(shnum)]
    ss=secs[shstrndx]
    nm=lambda n: bytes(d[ss[4]+n:d.index(0,ss[4]+n)]).decode()
    by={nm(s[0]):(i,s) for i,s in enumerate(secs)}
    ti,_=by['.text']; _,ds=by['.dynsym']; _,dstr=by['.dynstr']; hi,hs=by['.hash'] if '.hash' in by else by['.gnu.hash']
    # find used hash length
    B,N=struct.unpack_from('<II',d,hs[4]); used=(2+B+N)*4
    stub=hs[4]+((used+3)//4)*4; vaddr=hs[3]+(stub-hs[4])
    assert stub+8<=hs[4]+hs[5],'no room'
    for i in range(ds[5]//16):
        o=ds[4]+i*16
        so,val,sz,info,oth,shn=struct.unpack_from('<IIIBBH',d,o)
        if bytes(d[dstr[4]+so:d.index(0,dstr[4]+so)])==b'__register_atfork':
            struct.pack_into('<II',d,stub,0xE3A00000,0xE12FFF1E)  # mov r0,#0 ; bx lr
            struct.pack_into('<IIIBBH',d,o,so,vaddr,8,0x12,0,ti)
            print(path,'stub at',hex(vaddr),'sym',i); break
    else: print(path,'sym not found'); return
    open(path,'wb').write(d)
for p in sys.argv[1:]: patch(p)
