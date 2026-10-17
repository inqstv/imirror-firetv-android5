import struct,sys
def elfhash(n):
    h=0
    for c in n:
        h=((h<<4)+c)&0xffffffff
        g=h&0xf0000000
        if g: h^=g>>24
        h&=~g&0xffffffff
    return h
def patch(path):
    d=bytearray(open(path,'rb').read())
    shoff,=struct.unpack_from('<I',d,32); shentsize,shnum,shstrndx=struct.unpack_from('<HHH',d,46)
    secs=[]
    for i in range(shnum):
        n,t,f,a,o,s,l,inf,al,es=struct.unpack_from('<IIIIIIIIII',d,shoff+i*shentsize); secs.append((n,t,a,o,s,l,es))
    shstr=secs[shstrndx]
    def name(n):
        e=d.index(0,shstr[3]+n); return bytes(d[shstr[3]+n:e]).decode()
    by={name(s[0]):(i,s) for i,s in enumerate(secs)}
    _,ds=by['.dynsym']; _,gh=by['.gnu.hash']; _,dy=by['.dynamic']; _,dstr=by['.dynstr']
    nsym=ds[4]//16
    dyn=dy[3]; dynsz=dy[4]
    ents=[struct.unpack_from('<II',d,dyn+i*8) for i in range(dynsz//8)]
    if any(t==4 for t,_ in ents): print(path,'already has HASH'); return
    gi=[i for i,(t,_) in enumerate(ents) if t==0x6ffffef5]
    assert len(gi)==1
    avail=gh[4]
    B=1
    while (2+(B*2+1)+nsym)*4<=avail and B<257: B=B*2+1
    assert (2+B+nsym)*4<=avail,(B,nsym,avail)
    buckets=[0]*B; chain=[0]*nsym
    for i in range(1,nsym):
        so,=struct.unpack_from('<I',d,ds[3]+i*16)
        e=d.index(0,dstr[3]+so); nm=bytes(d[dstr[3]+so:e])
        h=elfhash(nm)%B
        chain[i]=buckets[h]; buckets[h]=i
    blob=struct.pack('<II',B,nsym)+struct.pack('<%dI'%B,*buckets)+struct.pack('<%dI'%nsym,*chain)
    off=gh[3]
    d[off:off+avail]=b'\0'*avail
    d[off:off+len(blob)]=blob
    struct.pack_into('<II',d,dyn+gi[0]*8,4,gh[2])  # DT_HASH -> same vaddr
    # section header type -> SHT_HASH
    idx=by['.gnu.hash'][0]
    struct.pack_into('<I',d,shoff+idx*shentsize+4,5)
    open(path,'wb').write(d)
    print(path,'patched B=%d nsym=%d'%(B,nsym))
for p in sys.argv[1:]: patch(p)
