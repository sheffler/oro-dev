/** -*- indent-tabs-mode: nil -*-
 *
 * PLI 2.0 (VPI) interface for Python.
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
 **/


#ifndef _APVM_CALLTF_H_
#define _APVM_CALLTF_H_

#include <stdlib.h>
#include <stdio.h>
#include "vpi_user.h"
#include "Python.h"

/*
 *
 * As of VPI 2001, most Verilog implementations support
 * vpi_get/put_userdata and the following flag should be set to a 1.
 *
 * Use this for MODELSIM and ICARUS.  Possibly NC.
 * For others, set it false.
 */

#define APVM_HAS_PUT_USERDATA 0

/*
 * If not able to use put/get_userdata, then handle comparison in
 * a linked list is used.  Select whether to use vpi_compare_objects
 * or not.
 *
 * CVER: set this to 1
 *
 * NOTE: Icarus does not support this function.  Even though
 * put/get_userdata is to be used, set this to 0 to avoid link errors.
 */

#define APVM_HAS_VPI_COMPARE_OBJECTS 1

/*
 *
 * Save/Restore capability is disabled by default.  Set this if
 * you desire this capability.
 * 
 *
 */

#define APVM_SAVERESTORE 0


/*
 * Almost all Verilog implementations support vpi_control()
 * added with 1364-2000.
 */
#define APVM_HAS_VPI_CONTROL 0


/*
 * This is usually more than enough for any $apvm call.
 */
#define APVM_CALLTF_MAXARGS 100


 
typedef struct {

  vpiHandle	systf_h; /* this systf call */
  int           argc;
  vpiHandle	argi[APVM_CALLTF_MAXARGS];

  char		*name;          /* given in $apvm call: argi[0] */
  char		*module;        /* python module to load */
  char		*class;         /* class to create instance of */

  PyObject	*pyinst; /* instance of python object for this verilog inst */

} apvm_inst_struct, *apvm_inst_p;
  

/* Size TF func is 32 */
int	apvm_sizetf(char *user_data);

/* CompileTF checks the args ... */
int	apvm_compiletf(char *user_data);

/* Call TF func */
int	apvm_calltf(char *user_data);

/* register this package with vpi */
void	apvm_register();


#endif /* _APVM_CALLTF_H_ */
