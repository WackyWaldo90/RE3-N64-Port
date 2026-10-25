#include "r3sc_bank.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char *readall(const char *path,size_t *n){FILE*f=fopen(path,"rb");long sz;unsigned char*b;assert(f);assert(fseek(f,0,SEEK_END)==0);sz=ftell(f);assert(sz>=0);rewind(f);b=malloc((size_t)sz);assert(b);assert(fread(b,1,(size_t)sz,f)==(size_t)sz);fclose(f);*n=(size_t)sz;return b;}
int main(int argc,char **argv){size_t ni,nb;unsigned char *idx,*bank;R3SCManager m;unsigned gen;char id[17]={0};assert(argc==3);idx=readall(argv[1],&ni);bank=readall(argv[2],&nb);memcpy(id,idx+16,16);r3sc_manager_init(&m);assert(r3sc_bank_activate(&m,idx,ni,bank,nb,id)==0);assert(m.room.count>0);gen=m.generation;assert(r3sc_bank_activate(&m,idx,ni,bank,nb,"NOT_A_ROOM")==-27);assert(m.generation==gen);bank[0]^=1;assert(r3sc_bank_activate(&m,idx,ni,bank,nb,id)==-24);assert(m.generation==gen);r3sc_manager_clear(&m);free(idx);free(bank);puts("ROM bank activation, missing room and corruption tests passed");return 0;}
