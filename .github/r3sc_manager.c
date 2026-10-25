#include "r3sc_manager.h"
#include <string.h>
void r3sc_manager_init(R3SCManager *m){if(m){m->room.count=0;m->room.records=NULL;m->active_id[0]='\0';m->generation=0;}}
void r3sc_manager_clear(R3SCManager *m){if(m){r3sc_free(&m->room);m->active_id[0]='\0';m->generation++;}}
int r3sc_manager_activate(R3SCManager *m,const char *id,const uint8_t *bytes,size_t length){
 size_t n;R3SCRoom next;int rc;
 if(!m||!id)return -10;
 n=strlen(id);
 if(n==0||n>R3SC_ROOM_ID_MAX)return -11;
 /* No assumptions about room identifiers beyond length. */
 rc=r3sc_load(bytes,length,&next);
 if(rc)return rc;
 r3sc_free(&m->room);
 m->room=next;
 memcpy(m->active_id,id,n+1);
 m->generation++;
 return 0;
}
const R3SCRecord *r3sc_manager_record(const R3SCManager *m,size_t i){
 if(!m||i>=m->room.count)return NULL;
 return &m->room.records[i];
}
