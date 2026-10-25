#ifndef R3SC_LOADER_H
#define R3SC_LOADER_H
#include <stddef.h>
#include <stdint.h>
typedef struct {int16_t x1,z1,x2,z2;uint16_t id,type,floor_mask,unknown;} R3SCRecord;
typedef struct {uint16_t count;R3SCRecord *records;} R3SCRoom;
/* Returns 0 on success. The caller owns the input bytes; call r3sc_free. */
int r3sc_load(const uint8_t *bytes,size_t length,R3SCRoom *out);
void r3sc_free(R3SCRoom *room);
#endif
