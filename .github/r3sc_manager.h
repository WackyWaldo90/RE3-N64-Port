#ifndef R3SC_MANAGER_H
#define R3SC_MANAGER_H
#include "r3sc_loader.h"
#include <stddef.h>
#include <stdint.h>
#define R3SC_ROOM_ID_MAX 31
/* Holds one active room. Caller must initialize with r3sc_manager_init. */
typedef struct { R3SCRoom room; char active_id[R3SC_ROOM_ID_MAX+1]; unsigned generation; } R3SCManager;
void r3sc_manager_init(R3SCManager *manager);
void r3sc_manager_clear(R3SCManager *manager);
/* Atomic room replacement: failures leave current room and generation untouched.
   bytes must point to the complete .r3sc file; ID is a caller-provided logical key.
   Returns 0 on success; negative on validation/loader failure. */
int r3sc_manager_activate(R3SCManager *manager,const char *id,const uint8_t *bytes,size_t length);
const R3SCRecord *r3sc_manager_record(const R3SCManager *manager,size_t index);
#endif
