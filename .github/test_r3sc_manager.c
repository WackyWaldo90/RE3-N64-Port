#include "r3sc_manager.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char *readfile(const char *path,size_t *len){
 FILE*f=fopen(path,"rb");long n;unsigned char*b;
 assert(f);assert(fseek(f,0,SEEK_END)==0);n=ftell(f);assert(n>=0);rewind(f);
 b=(unsigned char*)malloc((size_t)n);assert(b);assert(fread(b,1,(size_t)n,f)==(size_t)n);fclose(f);*len=(size_t)n;return b;
}
int main(int argc,char **argv){
 R3SCManager m;size_t n1,n2;unsigned char *a,*b;unsigned before;const R3SCRecord *r;
 if(argc!=3)return 2;
 a=readfile(argv[1],&n1);b=readfile(argv[2],&n2);
 r3sc_manager_init(&m);assert(m.room.count==0&&m.generation==0);
 assert(r3sc_manager_activate(&m,"roomA",a,n1)==0);
 assert(m.room.count>0);r=r3sc_manager_record(&m,0);assert(r);assert(r3sc_manager_record(&m,m.room.count)==NULL);
 before=m.generation;
 a[n1-1]^=1;
 assert(r3sc_manager_activate(&m,"bad",a,n1)<0);
 assert(m.generation==before&&strcmp(m.active_id,"roomA")==0&&m.room.count>0);
 assert(r3sc_manager_activate(&m,"roomB",b,n2)==0);
 assert(strcmp(m.active_id,"roomB")==0&&m.generation==before+1);
 assert(r3sc_manager_activate(&m,"",b,n2)<0);
 assert(strcmp(m.active_id,"roomB")==0);
 r3sc_manager_clear(&m);assert(m.room.count==0&&m.room.records==NULL&&m.active_id[0]==0);
 free(a);free(b);puts("PASS: swap, rollback, record access, clear");return 0;
}
