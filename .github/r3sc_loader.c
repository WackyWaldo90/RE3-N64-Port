#include "r3sc_loader.h"
#include <stdlib.h>
static uint16_t u16(const uint8_t*p){return (uint16_t)(((uint16_t)p[0]<<8)|p[1]);}
static uint32_t u32(const uint8_t*p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static uint32_t crc32_calc(const uint8_t *p,size_t n){
 uint32_t crc=0xffffffffu;size_t i;int j;
 for(i=0;i<n;i++){crc^=p[i];for(j=0;j<8;j++)crc=(crc>>1)^((crc&1)?0xedb88320u:0u);}
 return crc^0xffffffffu;
}
void r3sc_free(R3SCRoom *room){if(room){free(room->records);room->records=NULL;room->count=0;}}
int r3sc_load(const uint8_t *bytes,size_t length,R3SCRoom *out){
 size_t i;uint16_t count;uint32_t size;R3SCRecord *records;
 if(!out)return -1;
 out->count=0;out->records=NULL;
 if(!bytes||length<16)return -2;
 if(bytes[0]!='R'||bytes[1]!='3'||bytes[2]!='S'||bytes[3]!='C'||u16(bytes+4)!=1)return -3;
 count=u16(bytes+6);size=u32(bytes+8);
 if(size!=(uint32_t)count*16u||length!=(size_t)size+16u)return -4;
 if(crc32_calc(bytes+16,size)!=u32(bytes+12))return -5;
 records=count?(R3SCRecord*)calloc(count,sizeof(R3SCRecord)):NULL;
 if(count&&!records)return -6;
 for(i=0;i<count;i++){
  const uint8_t*p=bytes+16+i*16;
  records[i].x1=(int16_t)u16(p);records[i].z1=(int16_t)u16(p+2);
  records[i].x2=(int16_t)u16(p+4);records[i].z2=(int16_t)u16(p+6);
  records[i].id=u16(p+8);records[i].type=u16(p+10);
  records[i].floor_mask=u16(p+12);records[i].unknown=u16(p+14);
 }
 out->count=count;out->records=records;return 0;
}
