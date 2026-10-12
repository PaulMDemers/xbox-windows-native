/* Pinned GL4.0 texture references and known FBO closure. Read-only scalar rows. */
static bool x281_selected(uint64_t name,const uint64_t names[4])
{for(unsigned i=0;i<4;i++)if(name==names[i])return true;return false;}
static int x281_index(uint64_t value,const uint32_t *values,unsigned count)
{for(unsigned i=0;i<count;i++)if(value==values[i])return i;return -1;}
static bool x281_edges(const uint64_t (*rows)[8],unsigned count,unsigned roles,const uint64_t names[4])
{
    const uint32_t integers[]={0x85b5,0x8894,0x8895,0x88ed,0x88ef,0x8a28,0x8b8d,0x8c8f,0x8ca6,0x8ca7,0x8caa,0x8f36,0x8f37};
    const uint32_t targets[]={0x8068,0x8069,0x806a,0x84f6,0x8514,0x8c1c,0x8c1d,0x8c2c,0x900a,0x9104,0x9105};
    if(!rows || !count || count>(roles==8?8192u:180000u) || (roles!=6&&roles!=8))return false;
    for(unsigned i=0;i<4;i++) {
        if(!names[i] || names[i]>UINT32_MAX)return false;
        for(unsigned j=0;j<i;j++)if(names[i]==names[j])return false;
    }
    unsigned context_mask=0;
    for(unsigned h=0;h<count;h++)if(rows[h][0]==30) {
        const uint64_t *header=rows[h];if(header[1]<1 || header[1]>3)return false;
        unsigned role=header[1];
        if(role<1||role>3 || !(roles&(1u<<role)) || (context_mask&(1u<<role)) ||
           !header[2] || header[4]<1 || header[4]>256 || header[5]<1 || header[5]>64)return false;
        context_mask|=1u<<role;
        uint16_t texture_seen[256]={0};unsigned integer_seen=0;uint64_t attrib_seen=0;
        uint64_t draw=UINT64_MAX,read=UINT64_MAX,vao=UINT64_MAX,program=UINT64_MAX;
        for(unsigned n=0;n<count;n++) {
            const uint64_t *r=rows[n];if(r[1]!=role)continue;
            if(r[0]==31) {
                int bit=x281_index(r[2],integers,13);
                if(bit<0 || (integer_seen&(1u<<bit)))return false;
                integer_seen|=1u<<bit;
                if(r[2]==0x8ca6)draw=r[3];
                if(r[2]==0x8caa)read=r[3];
                if(r[2]==0x85b5)vao=r[3];
                if(r[2]==0x8b8d)program=r[3];
            } else if(r[0]==32) {
                int bit=x281_index(r[3],targets,11);
                if(bit<0 || r[2]>=header[4] || (texture_seen[r[2]]&(1u<<bit)) || x281_selected(r[4],names))return false;
                texture_seen[r[2]]|=1u<<bit;
            } else if(r[0]==33) {
                if(r[2]>=header[5] || (attrib_seen&(UINT64_C(1)<<r[2])))return false;
                attrib_seen|=UINT64_C(1)<<r[2];
            }
        }
        if(integer_seen!=8191 || attrib_seen!=(header[5]==64?UINT64_MAX:(UINT64_C(1)<<header[5])-1))return false;
        for(unsigned i=0;i<header[4];i++)if(texture_seen[i]!=2047)return false;
        unsigned bound_draw=(!draw && roles!=8),bound_read=(!read && roles!=8);
        for(unsigned n=0;n<count;n++)if(rows[n][0]==54&&rows[n][1]==role) {
            const uint64_t *f=rows[n];unsigned attachments=0,restores=0;uint64_t slots=0,limit=0;unsigned ds=0;
            if(f[3]>1)return false;
            bound_draw|=f[2]==draw;bound_read|=f[2]==read;
            for(unsigned j=0;j<n;j++)if(rows[j][0]==54&&rows[j][1]==role&&rows[j][2]==f[2])return false;
            for(unsigned j=0;j<count;j++)if(rows[j][1]==role&&rows[j][2]==f[2]) {
                const uint64_t *r=rows[j];
                if(r[0]==56) {
                    if(++restores>1 || !f[3] || r[3]!=r[4] || r[5]!=r[6] || r[7]<1 || r[7]>64)return false;
                    limit=r[7];
                } else if(r[0]==55) {
                    if(!f[3] || (r[4]!=0&&r[4]!=0x1702&&r[4]!=0x8d41) || (!r[4]&&r[5]) ||
                       (r[4]==0x1702&&x281_selected(r[5],names)))return false;
                    attachments++;
                    if(r[3]==0x8d00 || r[3]==0x8d20) {
                        unsigned bit=r[3]==0x8d00?1:2;if(ds&bit)return false;ds|=bit;
                    } else {
                        if(r[3]<0x8ce0 || r[3]>=0x8ce0+64 || (slots&(UINT64_C(1)<<(r[3]-0x8ce0))))return false;
                        slots|=UINT64_C(1)<<(r[3]-0x8ce0);
                    }
                }
            }
            if(f[3] && (restores!=1 || attachments!=limit+2 || ds!=3 || slots!=(limit==64?UINT64_MAX:(UINT64_C(1)<<limit)-1)))return false;
            if(!f[3] && (restores||attachments))return false;
        }
        if(!bound_draw||!bound_read)return false;
        unsigned bound_vao=(!vao && roles!=8),bound_program=(!program && roles!=8);
        for(unsigned n=0;n<count;n++)if(rows[n][1]==role) {
            if(rows[n][0]==57 && rows[n][2]==vao)bound_vao++;
            if(rows[n][0]==61 && rows[n][2]==program)bound_program++;
        }
        if(!bound_vao || !bound_program || (roles==8 && (bound_vao!=1 || bound_program!=1)))return false;
    }
    if(context_mask!=roles)return false;
    for(unsigned n=0;n<count;n++) {
        const uint64_t *r=rows[n];
        if((r[0]>=30&&r[0]<=33)||(r[0]>=52&&r[0]<=63)) {if(r[1]<1||r[1]>3||!(roles&(1u<<r[1])))return false;}
        if(r[0]==55 || r[0]==56) {
            unsigned parent=0;for(unsigned j=0;j<count;j++)parent+=rows[j][0]==54&&rows[j][1]==r[1]&&rows[j][2]==r[2];
            if(parent!=1)return false;
        }
        if(roles==8 && ((r[0]==40&&(x281_selected(r[3],names)||x281_selected(r[4],names)||x281_selected(r[5],names))) ||
                       (r[0]==64&&x281_selected(r[3],names))))return false;
    }
    return true;
}
