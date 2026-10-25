#include "r3sc_bank.h"
#include <string.h>
static uint16_t rd16(const uint8_t *p){return (uint16_t)(((uint16_t)p[0]<<8)|p[1]);}
static uint32_t rd32(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static uint32_t crc32_calc(const uint8_t *p,size_t n){uint32_t c=~0u;size_t i;int j;for(i=0;i<n;i++){c^=p[i];for(j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320u:0u);}return ~c;}
int r3sc_bank_activate(R3SCManager *m,const uint8_t *idx,size_t ni,const uint8_t *bank,size_t nb,const char *id){
 uint16_t count;size_t i,n;uint32_t expected;
 if(!m||!idx||!bank||!id)return -20;
 n=strlen(id);if(n==0||n>15)return -21;
 if(ni<16||memcmp(idx,"R3BK",4)||rd16(idx+4)!=1)return -22;
 count=rd16(idx+6);if(ni!=16u+(size_t)count*28u)return -23;
 if(rd32(idx+8)!=nb||crc32_calc(bank,nb)!=rd32(idx+12))return -24;
 for(i=0;i<count;i++){
  const uint8_t *e=idx+16+i*28;uint32_t off,len,crc;
  if(memcmp(e,id,n)||e[n]!=0)continue;
  off=rd32(e+16);len=rd32(e+20);crc=rd32(e+24);
  if(off%16||off>nb||len>nb-off)return -25;
  expected=crc32_calc(bank+off,len);if(expected!=crc)return -26;
  return r3sc_manager_activate(m,id,bank+off,len);
 }
 return -27;
}
