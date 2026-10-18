# SPDX-License-Identifier: MIT
"""Small bounded ELF32/i386 reader for retained build artifacts; no execution."""
import struct

def u32(b,n):return struct.unpack_from('<I',b,n)[0]
def string(b,n):
    if not 0<=n<len(b):raise ValueError('string offset')
    end=b.find(b'\0',n)
    if end<0:raise ValueError('unterminated string')
    return b[n:end].decode('ascii')

def parse(b):
    if len(b)<52 or b[:7]!=b'\x7fELF\x01\x01\x01' or struct.unpack_from('<H',b,18)[0]!=3:
        raise ValueError('ELF32/i386')
    off=u32(b,32);size,count,strings=struct.unpack_from('<HHH',b,46)
    if size!=40 or not 0<strings<count<=64 or off+count*40>len(b):raise ValueError('section table')
    sections=[struct.unpack_from('<10I',b,off+i*40) for i in range(count)]
    def data(s):
        if s[5]>16*1024*1024:raise ValueError('section size bound')
        if s[1]==8:return bytes(s[5])
        if s[4]+s[5]>len(b):raise ValueError('section extent')
        return b[s[4]:s[4]+s[5]]
    names=data(sections[strings]);named={string(names,s[0]):i for i,s in enumerate(sections)}
    tab=sections[named['.symtab']]
    if tab[9]!=16 or tab[5]%16 or not 0<tab[6]<count:raise ValueError('symbol table')
    raw=data(tab);snames=data(sections[tab[6]]);symbols=[]
    for i in range(0,len(raw),16):
        n,value,length,info,other,index=struct.unpack_from('<IIIBBH',raw,i)
        symbols.append(dict(name=string(snames,n),value=value,section=index,size=length))
    relocs=[]
    for s in sections:
        if s[1]!=9:continue
        if s[9]!=8 or s[5]%8 or not 0<s[7]<count or s[6]!=named['.symtab']:raise ValueError('relocation table')
        rb=data(s)
        for pos in range(0,len(rb),8):
            at,info=struct.unpack_from('<II',rb,pos)
            if info>>8>=len(symbols) or at+4>sections[s[7]][5] or info&255 not in (1,2):
                raise ValueError('relocation entry')
            relocs.append(dict(section=s[7],offset=at,kind=info&255,symbol=symbols[info>>8]))
    return dict(sections=sections,named=named,symbols=symbols,relocations=relocs,data=data)

def relocated(e,bases):
    result={index:bytearray(e['data'](e['sections'][index])) for index in bases}
    ledger=[]
    for r in e['relocations']:
        index=r['section']
        if index not in bases:raise ValueError('unknown relocation destination')
        s=r['symbol'];at=r['offset'];kind=r['kind'];add=u32(result[index],at)
        if s['section'] in bases:target=bases[s['section']]+s['value']
        elif s['section']==0xfff1:target=s['value']
        else:raise ValueError('unresolved relocation source')
        value=(target+add-(bases[index]+at if kind==2 else 0))&0xffffffff
        struct.pack_into('<I',result[index],at,value)
        ledger.append(dict(section=index,offset=at,address=bases[index]+at,kind=kind,
                           symbol=s['name'],symbol_section=s['section'],target=target,addend=add,value=value))
    return {i:bytes(b) for i,b in result.items()},ledger
