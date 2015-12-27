/*
 *
 * Core VPI support for APVM.
 *
 * Copyright (c) 2004 Tom Sheffler
 *
 *    This source code is free software; you can redistribute it
 *    and/or modify it in source code form under the terms of the GNU
 *    General Public License as published by the Free Software
 *    Foundation; either version 2 of the License, or (at your option)
 *    any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program; if not, write to the Free Software
 *    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include "apvm_core.h"

/*
 * All PLI functions sharing this core call this function to initalize
 * global APVM storage areas, and to cause the banner to print.
 */

static int apvm_core_initialized = 0;
static int apvm_cver_found = 0;

static int debugging = 0;

static s_vpi_vlog_info apvm_sim_info; /* struct with simulator info */

void apvm_core_init()
{
  if (!apvm_core_initialized) {
    apvm_core_initialized = 1;

    if (getenv("APVM_C_DEBUGGING") != NULL) {
      debugging = 1;
    }

    vpi_get_vlog_info(&apvm_sim_info);

    if (strncmp(apvm_sim_info.product, "Cver", 4) == 0) {
      apvm_cver_found = 1;
      fprintf(stderr, "***\n");
      fprintf(stderr, "*** APVM WARNING REGARDING CVER:\n");
      fprintf(stderr, "*** Only ONE $apvm() instance will be handled correctly.\n");
      fprintf(stderr, "***\n");
    }

    fprintf(stderr, "%s\n", _apvm_copyright);
    fprintf(stderr, "%s\n", _apvm_license);
  }
}

/*
 * List of vpi Handles
 */

typedef struct apvm_hlist {
  vpiHandle		h;
  void			*userdata;
  struct apvm_hlist	*next;
} apvm_hlist_s, *apvm_hlist_p;


/* This is the list of (vpihandle, userdata) pairs */

static apvm_hlist_p apvm_hlist_root = 0;
static int apvm_put_userdata_count = 0;

/*
 * This pair of functions is used with Verilogs that do not yet
 * support vpi_put/get_userdata.  Soon, all simulators will, and these
 * functions will be unnecessary, which is a good thing, because
 * this is an inefficient list.
 */

void apvm_put_userdata(vpiHandle h, void* userdata)
{
  apvm_hlist_p	p;

  apvm_put_userdata_count++;	/* Cver diagnosis */

  if (apvm_cver_found && apvm_put_userdata_count > 1) {
    fprintf(stderr, "Sorry.  Because of workarounds, only one $apvm instance is supported.\n");
    fprintf(stderr, "This is a Cver limitation at this point, but should be fixed soon.\n");
    exit(1);
  }

  if (debugging) {
    fprintf(stderr, "Inserting 0x%x\n", h);
  }

  p = (apvm_hlist_p) malloc(sizeof(apvm_hlist_s));

  p -> h = h;
  p -> userdata = userdata;
  p -> next = apvm_hlist_root;
  apvm_hlist_root = p;
}

void *apvm_get_userdata(vpiHandle h)
{
  apvm_hlist_p	p;
  int x;

  p = apvm_hlist_root;

  while (p != 0) {

    if (debugging) {
      fprintf(stderr, "APVM_GET_USERDATA: Comparing 0x%x, 0x%x ... ", h, p->h);
    }

#if APVM_HAS_VPI_COMPARE_OBJECTS
    x = vpi_compare_objects(h, p->h);
#else
    x = (h == p->h);
#endif

    if (debugging) {
      fprintf(stderr, "vpi_compare result: %d\n", x);
    }

    if (x || apvm_cver_found) {
      return p->userdata;
    }

    p = p->next;
  }
  return 0;
}
