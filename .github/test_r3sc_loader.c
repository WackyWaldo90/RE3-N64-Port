#include "r3sc_loader.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char**argv){
 FILE*f;long size;unsigned char*b;R3SCRoom room;int rc;
 if(argc!=2)return 2;
 f=fopen(argv[1],"rb");if(!f)return 3;
 assert(fseek(f,0,SEEK_END)==0);size=ftell(f);rewind(f);
 b=(unsigned char*)malloc((size_t)size);assert(b);
 assert(fread(b,1,(size_t)size,f)==(size_t)size);fclose(f);
 rc=r3sc_load(b,(size_t)size,&room);assert(rc==0);assert(room.count>0);
 printf("loaded %u records, first shape %u\\n",room.count,room.records[0].id&15u);
 b[size-1]^=1;assert(r3sc_load(b,(size_t)size,&room)!=0);
 free(b);return 0;
}
