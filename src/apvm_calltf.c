/* -*- indent-tabs-mode: nil -*-
 *
 * PLI 2.0 (VPI) interface for Python
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
 */


#include <stdlib.h>
#include <stdio.h>
#include <strings.h>

#include "apvm_malloc.h"
#include "apvm_core.h"
#include "apvm_calltf.h"

#include "Python.h"  

#define APVM_MODULE_NAME "_apvm"

/*
 * This will be our exception
 */
static PyObject *apvm_vpi_error;

/*
 * For debugging
 */
static int debugging = 0;

/*
 *
 * Forward Declarations
 *
 */

static int apvm_soscb(p_cb_data);
static int apvm_othercb(p_cb_data);
static int apvm_callback(p_cb_data);
void initapvm_vpi();
static PyObject* deconstruct_p_cb_data(p_cb_data cb);
     

/*
 *
 * type strings for the CObject descriptions
 *
 */

static char *cob_callbackfn_desc = "apvm_callback_PyCObject";
static char *cob_vpiHandle_desc = "vpiHandle_PyCObject";
static char *cob_vpi_time_desc = "s_vpi_time_PyCObject";
static char *cob_vpi_value_desc = "s_vpi_value_PyCObject";
static char *cob_vpi_cb_data_desc = "s_cb_data_PyCObject";


/*
 *
 * Size is a constant - 32 bits
 *
 */
int apvm_sizetf(char *user_data)
{
  if (debugging) {
    fprintf(stderr, "+++ APVM - in SIZETF\n");
  }

  return 32;
}

/*
 * Insert this function after every vpi_ call to check status.
 */
static int chkvpierr()
{
  s_vpi_error_info info;
  int level;

  if ((level = vpi_chk_error(&info)) != 0) {
    fprintf(stderr, "+++ APVM VPI ERROR +++ level %d\n", level);
    fprintf(stderr, "+++ MESS: %s\n", info.message);
    fprintf(stderr, "+++ PROD: %s\n", info.product);
    fprintf(stderr, "+++ CODE: %s\n", info.code);
    fprintf(stderr, "+++ FILE: %s\n", info.file);
    fprintf(stderr, "+++\n");
  }
  return level;
}


/*
 *
 * The compile function simply does nothing with the arguments,
 * but it does the very important step of registering the soscb.
 *
 * Format of call should be:
 *   res = $apvm("name", "module", "class", v1, v2, v3, ...);
 *
 */

int apvm_compiletf(char *user_data)
{
  int		i;
  vpiHandle     systf_h;
  vpiHandle     arg_iterator, arg_h;
  int           tfarg_type;
  s_cb_data     start_of_sim;
  vpiHandle	argi[APVM_CALLTF_MAXARGS];

  if (getenv("APVM_C_DEBUGGING") != NULL) {
    fprintf(stderr, "+++ APVM - in COMPILETF\n");
  }

  systf_h = vpi_handle(vpiSysTfCall, NULL); /* this fn */
  chkvpierr();

  arg_iterator = vpi_iterate(vpiArgument, systf_h);
  chkvpierr();
  i = 0;

  if (arg_iterator == NULL) {
    apvm_msgerr("ERROR: missing argument list to $apvm(...)");
  }

  /* Copy args pointers into argi array */
  while ((argi[i] = vpi_scan(arg_iterator)) != NULL) {
    chkvpierr();
    i++;
  }
  /* iterator is exhausted, no need to free */

  /* Check ARG0 - either string constant, or reg instance */
  arg_h = argi[0];
  tfarg_type = vpi_get(vpiType, arg_h);
  chkvpierr();
  if (arg_h && tfarg_type != vpiConstant) {
    if (arg_h && tfarg_type != vpiReg) {
      vpi_printf("ERROR: Arg1 to $apvm must be instance name string or register\n");
      vpi_printf("  It is type %d\n", tfarg_type);
      /* tf_dofinish(); */
      exit(1);
    }
  }

  /* Check ARG1 - string constant */
  arg_h = argi[1];
  tfarg_type = vpi_get(vpiType, arg_h);
  chkvpierr();
  if (arg_h && tfarg_type != vpiConstant) {
    vpi_printf("ERROR: Arg2 to $apvm must be module name.\n");
    vpi_printf("  It is type %d\n", tfarg_type);
    /* tf_dofinish(); */
    exit(1);
  }

  /* Check ARG2 - string constant */
  arg_h = argi[2];
  tfarg_type = vpi_get(vpiType, arg_h);
  chkvpierr();
  if (arg_h && tfarg_type != vpiConstant) {
    vpi_printf("ERROR: Arg3 to $apvm must be class name.\n");
    vpi_printf("  It is type %d\n", tfarg_type);
    /* tf_dofinish(); */
    exit(1);
  }

  if (debugging) {
    fprintf(stderr, "+++ APVM: COMPILETF - before vpi_register_cb\n");
  }

  /* Schedule start of sim callback */
  /* start_of_sim.reason = cbEndOfCompile; */
  /* Tried this for CVER - no change */
  /* start_of_sim.reason = cbStartOfSimulation; */
  start_of_sim.reason = cbEndOfCompile;
  start_of_sim.cb_rtn = apvm_soscb;
  start_of_sim.obj = NULL;
  start_of_sim.time = NULL;
  start_of_sim.value = NULL;
  start_of_sim.index = 0;
  start_of_sim.user_data = (char*) systf_h;
  vpi_register_cb(&start_of_sim);
  chkvpierr();


  /* Schedule end of sim callback */
  start_of_sim.reason = cbEndOfSimulation;
  start_of_sim.cb_rtn = apvm_othercb;
  start_of_sim.obj = NULL;
  start_of_sim.time = NULL;
  start_of_sim.value = NULL;
  start_of_sim.index = 0;
  start_of_sim.user_data = (char*) systf_h;
  vpi_register_cb(&start_of_sim);

  chkvpierr();

#if APVM_SAVERESTORE

  /* Schedule Start Of Save callback */
  start_of_sim.reason = cbStartOfSave;
  start_of_sim.cb_rtn = apvm_othercb;
  start_of_sim.obj = NULL;
  start_of_sim.time = NULL;
  start_of_sim.value = NULL;
  start_of_sim.index = 0;
  start_of_sim.user_data = (char*) systf_h;
  vpi_register_cb(&start_of_sim);
  chkvpierr();

  /* Schedule End Of Save callback */
  start_of_sim.reason = cbEndOfSave;
  start_of_sim.cb_rtn = apvm_othercb;
  start_of_sim.obj = NULL;
  start_of_sim.time = NULL;
  start_of_sim.value = NULL;
  start_of_sim.index = 0;
  start_of_sim.user_data = (char*) systf_h;
  vpi_register_cb(&start_of_sim);
  chkvpierr();

  /* Schedule Start Of Restart callback */
  start_of_sim.reason = cbStartOfRestart;
  start_of_sim.cb_rtn = apvm_othercb;
  start_of_sim.obj = NULL;
  start_of_sim.time = NULL;
  start_of_sim.value = NULL;
  start_of_sim.index = 0;
  start_of_sim.user_data = (char*) systf_h;
  vpi_register_cb(&start_of_sim);
  chkvpierr();

  /* Schedule End Of Restart callback */
  start_of_sim.reason = cbEndOfRestart;
  start_of_sim.cb_rtn = apvm_othercb;
  start_of_sim.obj = NULL;
  start_of_sim.time = NULL;
  start_of_sim.value = NULL;
  start_of_sim.index = 0;
  start_of_sim.user_data = (char*) systf_h;
  vpi_register_cb(&start_of_sim);
  chkvpierr();

#endif  /* APVM_SAVERESTORE */

  return 0;
}


/*
 *
 * Initialize PY
 *
 */

static apvm_is_initialized = 0;

static int apvm_soscb(p_cb_data cbdata)
{
  vpiHandle     systf_h;
  vpiHandle     arg_iterator, argi[APVM_CALLTF_MAXARGS];
  s_vpi_value   argval;
  int           i;
  int           tfarg_type;
  apvm_inst_p pp;
  char          *plusarg;
  char          **plusarglist;
  vpiHandle     scope_h;        /* current scope */
  int           timeunit, precision;

  /*
   * Allow turning on C debugging with an env variable.
   */
  if (getenv("APVM_C_DEBUGGING") != NULL) {
    debugging = 1;
  }

  if (debugging) {
    fprintf(stderr, "+++ APVM: Before apvm_core_init\n");
  }

  /* initialize core VPI sys func support */
  apvm_core_init();

  if (debugging) {
    fprintf(stderr, "+++ APVM: After apvm_core_init\n");
  }

  /* Get TF instance for which this is called back */
  systf_h = (vpiHandle) cbdata->user_data;

  if (debugging) {
    fprintf(stderr, "+++ APVM: before arg iter\n");
  }

  arg_iterator = vpi_iterate(vpiArgument, systf_h);
  chkvpierr();

  if (arg_iterator == NULL) {
    apvm_msgerr("ERROR: missing argument list to $apvm(...)");
  }
  
  /* Simply gather up all the args to simplify later processing */
  i = 0;
  while ((argi[i] = vpi_scan(arg_iterator)) != NULL) {
    chkvpierr();
    i++;
  }
  /* iterator is exhausted, no need to free w/ vpi_free_object */

  if (debugging) {
    fprintf(stderr, "+++ APVM: Got %d args\n", i);
  }

  /* Allocate our instance specific struct */
  pp = (apvm_inst_p) apvm_malloc(sizeof(apvm_inst_struct));

  /* Set our workarea */

  /*
   * As of Cver 1.10i - put_userdata does not work as I want,
   * but the hlist option is viable.
   *
   * Re - Cver 2.00 - it still doesn't work correctly.  See workaround
   * in apvm_core.c.
   *
   * apvm_put/get_userdata has workaround for Cver
   *
   */

#if APVM_HAS_PUT_USERDATA
  vpi_put_userdata(systf_h, pp);
  chkvpierr();  
#else
  apvm_put_userdata(systf_h, (void*) pp);
#endif

  /* Initialize the struct */
  pp->systf_h = systf_h;

  /* Get name string value */
  if (argi[0]) {
    tfarg_type = vpi_get(vpiType, argi[0]);
    chkvpierr();
    if (tfarg_type == vpiConstant) {
      argval.format = vpiStringVal;
      vpi_get_value(argi[0], &argval);
      chkvpierr();
      pp->name = apvm_strdup(argval.value.str);
    }
    else {
      /* assume is reg and we use the path */
      pp->name = apvm_strdup(vpi_get_str(vpiFullName, argi[0]));
      chkvpierr();
    }
      
    if (debugging) {
      fprintf(stderr, "+++ APVM: PY NAME:%s\n", pp->name);
    }
  }

  /* Get module string value */
  if (argi[1]) {
    argval.format = vpiStringVal;
    vpi_get_value(argi[1], &argval);
    chkvpierr();
    pp->module = apvm_strdup(argval.value.str);
    if (debugging) {
      fprintf(stderr, "+++ APVM: PY MODULE:%s\n", pp->module);
    }
  }

  /* Get class string value */
  if (argi[2]) {
    argval.format = vpiStringVal;
    vpi_get_value(argi[2], &argval);
    chkvpierr();
    pp->class = apvm_strdup(argval.value.str);
    if (debugging) {
      fprintf(stderr, "+++ APVM: PY class:%s\n", pp->class);
    }
  }

  /* Move the rest of the argi down */
  i = 0;
  while ((pp->argi[i] = argi[i+3]) != NULL) {
    i++;
  }

  pp->argc = i;                 /* arg count */
  pp->pyinst = NULL;            /* our Py object is filled in next */

  do_py_initialization(pp);
}


/*
 *
 * This function handles the Python side of initializing the
 * instance.  It imports the module, calls the class and stores
 * the handle of the Python instance in the pp.
 *
 */

int do_py_initialization(apvm_inst_p pp)
{

  PyObject *pName, *pModule, *pDict, *pFunc;
  PyObject *pArgs, *pValue;
  char *apvm_prerun;

  if (apvm_is_initialized == 0) {
    if (debugging) {
      fprintf(stderr, "+++ APVM: Just before Py_Initialize\n");
    }
    Py_Initialize();

    /* See if there is a pre-run command */
    apvm_prerun = getenv("APVM_PRERUN_HOOK");
    if (apvm_prerun != NULL) {
      if (debugging) {
        fprintf(stderr, "+++ APVM: Running prerun hook: %s\n", apvm_prerun);
      }
      PyRun_SimpleString(apvm_prerun);
    }

    /* Add our module*/
    initapvm_vpi();

    if (debugging) {
      fprintf(stderr, "+++ APVM: Just after Py_Initialize\n");
    }
    apvm_is_initialized = 1;
  }

  pName = PyString_FromString(pp->module);
  /* Error checking of pName omitted */

  pModule = PyImport_Import(pName);
  if (pModule != NULL) {

    if (debugging) {
      fprintf(stderr, "+++ APVM: successfully loaded module: %s\n", pp->module);
    }

    pDict = PyModule_GetDict(pModule);
    /* pDict is a borrowed reference */

    pFunc = PyDict_GetItemString(pDict, pp->class);
    /* pFunc is borrowed reference */

    if (pFunc && PyCallable_Check(pFunc)) {
      pArgs = PyTuple_New(6);

      pValue = PyCObject_FromVoidPtrAndDesc((void*) pp->systf_h, cob_vpiHandle_desc, NULL);
      if (!pValue) {
        apvm_msgerr("Cannot create PyCObject from systf_h vpiHandle");
      }
      PyTuple_SetItem(pArgs, 0, pValue);

      pValue = PyCObject_FromVoidPtrAndDesc((void*) apvm_callback, cob_callbackfn_desc, NULL);
      if (!pValue) {
        apvm_msgerr("Cannot create PyCObject for callback function.");
      }
      PyTuple_SetItem(pArgs, 1, pValue);
      
      pValue = PyString_FromString(pp->name);
      if (!pValue) {
	apvm_msgerr("cannot convert arg 1");
      }
      PyTuple_SetItem(pArgs, 2, pValue);

      pValue = PyString_FromString(pp->module);
      if (!pValue) {
	apvm_msgerr("cannot convert arg 2");
      }
      PyTuple_SetItem(pArgs, 3, pValue);

      pValue = PyString_FromString(pp->class);
      if (!pValue) {
	apvm_msgerr("cannot convert arg 3");
      }
      PyTuple_SetItem(pArgs, 4, pValue);

      {
        PyObject *pVobjs;
        int i;
        pVobjs = PyTuple_New(pp->argc);
        for (i = 0; i < pp->argc; i++) {
          pValue = PyCObject_FromVoidPtrAndDesc((void*) (pp->argi[i]), cob_vpiHandle_desc, NULL);
          if (!pValue) {
            apvm_msgerr("Problem converting vpiHandle to PyCObject");
          }
          PyTuple_SetItem(pVobjs, i, pValue);
        }
        PyTuple_SetItem(pArgs, 5, pVobjs);
      }

      /* Call our class constructor */
      pValue = PyObject_CallObject(pFunc, pArgs);

      if (pValue != NULL) {
        if (debugging) {

          /* TOM: finally figured it out.  Calling PyString_AsString for debugging
           * output causes memory corruption problems.  Need to understand sometime.
           */
#if 0
          fprintf(stderr, "+++ APVM: Result of Class Constructor pycall: %0x, %s\n", pValue,
                      PyString_AsString(pValue));
#else
          fprintf(stderr, "+++ APVM: Result of Class Constructor pycall: %0x\n", pValue);
#endif
          
        }
	/* TOM: I don't want to decref this - i want to hang on to it!!! */
	/* Py_DECREF(pValue); */
	pp->pyinst = pValue;
      }
      else {
	PyErr_Print();
	apvm_msgerr("Pycall failed :-( (init)\n");
      }
      Py_DECREF(pArgs);
      /* pDict and pFunc are borrowed and must not be decref'd */

    }
    else {
      PyErr_Print();
      apvm_msgerr("Cannot find class \"%s\"\n", pp->class);
    }
  }
  else {
    PyErr_Print();
    apvm_msgerr("Failed to load python module \"%s\"\n", pp->module);
  }
  Py_DECREF(pName);
}


int apvm_calltf(char *user_data)
{
  vpiHandle             systf_h;
  s_vpi_value		vpival; /* get/set register values */
  s_vpi_value           retval; /* systf return value */
  int                   iretval;
  double		time;
  
  apvm_inst_p	pp;
  int                   success;

  PyObject *pFunc, *pArgs, *pValue;

  /* Get handle to this instance, look up our workarea */
  systf_h = vpi_handle(vpiSysTfCall, NULL);
  chkvpierr();

#if APVM_HAS_PUT_USERDATA
  if ((pp = vpi_get_userdata(systf_h)) == 0) {
    chkvpierr();
#else    
  if ((pp = (apvm_inst_p) apvm_get_userdata(systf_h)) == 0) {
#endif
    fflush(stdout);
    fprintf(stderr, "APVM INTERNAL ERROR: Workarea not found for handle %d in calltf.\n", systf_h);
    exit(1);
  }

  pValue = PyObject_CallMethod(pp->pyinst, "calltf", NULL);

  if (pValue != NULL) {
    iretval = PyInt_AsLong(pValue);
    if (debugging) {
      fprintf(stderr, "+++ APVM: Result of calltf pycall: %0x, %d\n", pValue, iretval);
    }
    retval.format = vpiIntVal;
    retval.value.integer = iretval;
    vpi_put_value(systf_h, &retval, NULL, vpiNoDelay);
    chkvpierr();
    Py_DECREF(pValue);
  }
  else {
    /* NOTE: there may not be a value because of arbitrary fail */
    PyErr_Print();
    apvm_msgerr("Pycall calltf failed to provide return val :-(\n");
  }
}


/*
 * This package registers some standard callbacks for all systf instances,
 * making it easy to implement behavior for a systf if it is so desired.
 * While some simulators may not implement all of these callbacks,
 * we attempt to register them anyway.
 *
 * Return values from the methods are simply ignored.
 */

static int apvm_othercb(p_cb_data cbdata)
{
  vpiHandle             systf_h;
  s_vpi_value		vpival;	/* get/set register values */
  s_vpi_value           retval; /* systf return value */
  int                   iretval;
  double		time;
  char                  *method;
  
  apvm_inst_p	pp;
  int                   success;

  PyObject *pFunc, *pArgs, *pValue;

  if (debugging) {
    fprintf(stderr, "+++ APVM: PY OTHERCB - %d\n", cbdata->reason);
  };

  if (cbdata->reason == cbStartOfRestart) {
    if (debugging) {
      fprintf(stderr, "+++ APVM: START OF RESTART\n");
    }
    /* is like start-of-sim */
    apvm_soscb(cbdata);
  }
    

  /* Get handle to this instance, look up our workarea */
  systf_h = (vpiHandle) cbdata->user_data;
  chkvpierr();

#if APVM_HAS_PUT_USERDATA
  if ((pp = vpi_get_userdata(systf_h)) == 0) {
    chkvpierr();
#else
  if ((pp = (apvm_inst_p) apvm_get_userdata(systf_h)) == 0) {
#endif
    fflush(stdout);
    fprintf(stderr, "APVM INTERNAL ERROR: Workarea not found for handle %d in othercb.\n", systf_h);
    exit(1);
  }

  /* Select which method to call */
  switch(cbdata->reason) {
  case cbEndOfSimulation:
    method = "eoscb";
    break;
  case cbStartOfSave:
    method = "StartOfSave";
    break;
  case cbEndOfSave:
    method = "EndOfSave";
    break;
  case cbStartOfRestart:
    method = "StartOfRestart";
    break;
  case cbEndOfRestart:
    method = "EndOfRestart";
    break;
  default:
    apvm_msgerr("Unimplemented callback called! %d\n", cbdata->reason);
    return 0;
  }

  pValue = PyObject_CallMethod(pp->pyinst, method, NULL);
  
  if (pValue != NULL) {
    Py_DECREF(pValue);
  }
  else {
    /* NOTE: there may not be a value because of arbitrary fail */
    PyErr_Print();
    apvm_msgerr("Pycall othercallback failed to provide return val :-(\n");
  }
}
  
static int apvm_callback(p_cb_data cbdata)
{
  vpiHandle             systf_h;
  s_vpi_value		vpival;	/* get/set register values */
  s_vpi_value           retval; /* systf return value */
  double		time;
  
  apvm_inst_p	pp;
  int                   success;

  PyObject *pName, *pModule, *pDict, *pFunc, *pArgs, *pValue;
  PyObject *pcbdata;

  if (debugging) {
    fflush(stdout);
    fprintf(stderr, "+++ APVM: In CALLBACK: %0x\n", cbdata);
    fprintf(stderr, "+++ Callback CB: %d %0x %0x %0x %0x\n", cbdata->reason, cbdata->cb_rtn, cbdata->obj, cbdata->time, cbdata->value);
  }

  pName = PyString_FromString(APVM_MODULE_NAME);
  /* Error checking of pName omitted */

  pModule = PyImport_Import(pName);
  if (pModule != NULL) {
    pDict = PyModule_GetDict(pModule);
    /* pDict is a borrowed reference */
    
    pFunc = PyDict_GetItemString(pDict, "generic_callback");

    if (pFunc && PyCallable_Check(pFunc)) {
      pArgs = PyTuple_New(1);

      /* Turn our callback data into something that python can manipulate */
      pcbdata = deconstruct_p_cb_data(cbdata);
      PyTuple_SetItem(pArgs, 0, pcbdata);

      pValue = PyObject_CallObject(pFunc, pArgs);

      /* TOM: 06/17/2004 */
      Py_DECREF(pArgs);

      if (pValue != NULL) {
        if (debugging) {
#if 0
          fprintf(stderr, "+++ APVM: Result of callback pycall: %0x, %s\n", pValue,
                  PyString_AsString(pValue));
#else 
          fprintf(stderr, "+++ APVM: Result of callback pycall: %0x\n", pValue);
#endif
        }
        Py_DECREF(pValue);
        /* pDict and pFunc are borrowed and must not be decref'd */
      }
      else {
        PyErr_Print();
        apvm_msgerr("Pycall callback failed to provide return value:-(\n");
      }
    }
    else {
      PyErr_Print();
      apvm_msgerr("Cannot find callback function \"%s\"\n", pp->class);
    }
  }
  else {
    PyErr_Print();
    apvm_msgerr("Failed to load python module \"%s\"\n", APVM_MODULE_NAME);
  }
  Py_DECREF(pName);
}


/*
 * Register the $apvm system function with Verilog.
 */

void apvm_register()
{
  s_vpi_systf_data      tfdata;

  if (getenv("APVM_C_DEBUGGING") != NULL) {
    fprintf(stderr, "+++ APVM - in APVM_REGISTER\n");
  }

  tfdata.type           = vpiSysFunc;

  /*
   * TOM: sysfunctype field seems to be problematic for different simulators!
   *  some simulators simply don't register callback if subtype missing.
   *
   * Icarus - doesn't implement vpiSizedFunc, so use vpiIntFunct.
   * CVER - use vpiIntFunc
   * MTI - use vpiSizedFunc or vpiIntFunc.
   * XL/NC - doesn't matter
   * VCS - doesn't matter
   *
   */

  tfdata.sysfunctype    = vpiIntFunc;
  /* tfdata.sysfunctype    = vpiSizedFunc; */
 
  tfdata.tfname         = "$apvm";
  tfdata.calltf         = apvm_calltf;
  tfdata.compiletf      = apvm_compiletf;
  /* tfdata.sizetf         = apvm_sizetf; */
  tfdata.sizetf         = 0;
  tfdata.user_data      = 0;

  vpi_register_systf(&tfdata);
  chkvpierr();
}

/****************************************************************
 *
 * The above code dealt with calling Py from Verilog.  The
 * below creates a new Python module "apvm_vpi" that has some basic
 * VPI definitions in it.
 *
 ****************************************************************/

/*
 * Most of this code consists of putting C pointers in Python PyCObject
 * structs and getting them back out.  We use the "description" field
 * of the PyCObject as a type descriptor so that we can perform minimal
 * error checking.
 */
static int
cob_check_typ(PyObject * obj, char *typ)
{
  if (((char*) PyCObject_GetDesc(obj)) != typ) {
    /* TOM: this needs to fit into the python error mechanism */
    apvm_msgerr("arg is not of PyCObject type %s, it is %s\n", typ, (char*)PyCObject_GetDesc(obj));
    return 0;
  }
  else {
    return 1;
  }
}

/*
 * If putting a malloc'd pointer into a PyCObject, this function
 * can be used to free it.
 */
static void apvm_malloc_destructor(void *obj, void *desc)
{
  apvm_free(obj);
}

/*
 * This can be used for vpiHandles.
 */
static void vpihandle_destructor(void *obj, void *desc)
{
  vpi_free_object(obj);
  chkvpierr();
}


static char get_val_bin_str_desc[] =
"Get the value of a vpiHandle as a binary string.";

static PyObject *
get_val_bin_str(PyObject *self, PyObject *args)
{
  vpiHandle     h;
  s_vpi_value   vpival;

  h = (vpiHandle) PyCObject_AsVoidPtr(PyTuple_GetItem(args, 0));

  vpival.format = vpiBinStrVal;
  vpi_get_value(h, &vpival);
  chkvpierr();

  return PyString_FromString(vpival.value.str);
}

/*
 * Construct/deconstruct opaque s_vpi_time object from Py args.
 *   Tuple: (lo, hi, real)
 */

static char construct_s_vpi_time_desc[] =
"pack_s_vpi_time(int, int, int, float) -> s_vpi_time opaque C object\n\
\n\
Construct an opaque s_vpi_time object from Python arguments of the types\n\
shown above.  The opaque s_vpi_time object may be turned back into its\n\
Python representation with deconstruct_s_vpi_time.";


static PyObject*
construct_s_vpi_time(PyObject *self, PyObject *args)
{
  /* PLI_UINT32 typ, lo, hi; */
  unsigned int typ, lo, hi;
  double real;
  p_vpi_time t;
  PyObject *pValue;

  typ = PyInt_AsLong(PyTuple_GetItem(args, 0));
  /* TOM: bug fix Jan 2005 */
  /* lo = PyInt_AsLong(PyTuple_GetItem(args, 1)); */
  lo = PyLong_AsUnsignedLong(PyTuple_GetItem(args, 1));
  /* hi = PyInt_AsLong(PyTuple_GetItem(args, 2)); */
  hi = PyLong_AsUnsignedLong(PyTuple_GetItem(args, 2));
  /* The user must make the types work */
  real = PyFloat_AsDouble(PyTuple_GetItem(args, 3));

  t = (p_vpi_time) apvm_malloc(sizeof(s_vpi_time));
  t->type = typ;
  t->high = hi;
  t->low = lo;
  t->real = real;

  /* Use description as object type tag for error checking later */
  pValue = PyCObject_FromVoidPtrAndDesc((void*) t, cob_vpi_time_desc, apvm_malloc_destructor);

  return pValue;
}


static PyObject*
deconstruct_p_vpi_time(p_vpi_time t)
{
  PyObject *tup, *pVal;

  tup = PyTuple_New(4);

  pVal = PyInt_FromLong(t->type);
  if (!pVal) {
    fprintf(stderr, "+++ APVM: Cannot get t->type from p_vpi_time\n");
  }
  PyTuple_SetItem(tup, 0, pVal);

  /* TOM: bug fix Jan 2005 */
  /* pVal = PyInt_FromLong(t->low); */
  pVal = PyLong_FromUnsignedLong(t->low);
  if (!pVal) {
    fprintf(stderr, "+++ APVM: Cannot get t->low from p_vpi_time\n");
  }
  PyTuple_SetItem(tup, 1, pVal);

  /* pVal = PyInt_FromLong(t->high); */
  pVal = PyLong_FromUnsignedLong(t->high);
  if (!pVal) {
    fprintf(stderr, "+++ APVM: Cannot get t->high from p_vpi_time\n");
  }
  PyTuple_SetItem(tup, 2, pVal);

  pVal = PyFloat_FromDouble(t->real);
  if (!pVal) {
    fprintf(stderr, "+++ APVM: Cannot get t->real from p_vpi_time\n");
  }
  PyTuple_SetItem(tup, 3, pVal);

  return tup;
}

static char deconstruct_s_vpi_time_desc[] =
"unpack_s_vpi_time(s_vpi_time object) -> (int, int, float)\n\
\n\
Given a pointer to an opaque C object that is a VPI s_vpi_time struct,\n\
return its representation as a Python tuple of the types shown\n\
above.";

  
static PyObject*
deconstruct_s_vpi_time(PyObject *self, PyObject *args)
{
  p_vpi_time t;

  if (debugging) {
    fprintf(stderr, "+++ APVM: In deconstruct_s_vpi_time: %0x\n", args);
  }
  if (((char*) PyCObject_GetDesc(PyTuple_GetItem(args, 0))) != cob_vpi_time_desc) {
    apvm_msgerr("arg to deconstruct_s_vpi_time is not correct type\n");
    PyErr_SetString(apvm_vpi_error, "arg to deconstruct_s_vpi_time");
  }
  t = (p_vpi_time) PyCObject_AsVoidPtr(PyTuple_GetItem(args, 0));
  if (!t) {
    apvm_msgerr("Cannot get p_vpi_time from PyCObject\n");
    PyErr_SetString(apvm_vpi_error, "cannot get p_vpi_time from PyCObject");
  }

  return deconstruct_p_vpi_time(t);
}


/*
 * Construct/deconstruct s_vpi_value struct.
 *  Tuple: (type, value)
 */

static char construct_s_vpi_value_desc[] =
"pack_s_vpi_value(type, value) -> s_vpi_value opaque C object\n\
\n\
type is one of the VPI constants vpiBinStrVal, vpiHexStrVal, etc.\n\
value is placed into the union field of the s_vpi_value based on\n\
its type.";


static PyObject *
construct_s_vpi_value(PyObject *self, PyObject *args)
{
  unsigned long format;
  char *str;
  unsigned int scalar;
  unsigned int integer;
  double real;
  s_vpi_time *time;
  s_vpi_vecval *vector;
  s_vpi_strengthval *strength;
  /* PLI_BYTE8 *misc; */
  unsigned char *misc;

  p_vpi_value p;
  PyObject *pVal;
  
  format = PyInt_AsLong(PyTuple_GetItem(args, 0));

  p = (p_vpi_value) apvm_malloc(sizeof(s_vpi_value));
  p->format = format;

  switch (format) {
  case vpiBinStrVal:
  case vpiOctStrVal:
  case vpiDecStrVal:
  case vpiHexStrVal:
    p->value.str = PyString_AsString(PyTuple_GetItem(args, 1));
    break;

  case vpiIntVal:
    p->value.integer = PyInt_AsLong(PyTuple_GetItem(args, 1));
    break;

  case vpiRealVal:
    p->value.real = PyFloat_AsDouble(PyTuple_GetItem(args, 1));
    break;

  case vpiStringVal:
    p->value.str = PyString_AsString(PyTuple_GetItem(args, 1));
    break;

  case vpiSuppressVal:
    p->value.integer = 0;
    break;

  default:
    PyErr_SetString(apvm_vpi_error, "don't know what in construct_s_vpi_value");
    return NULL;
  }

  pVal = PyCObject_FromVoidPtrAndDesc((void*) p, cob_vpi_value_desc, apvm_malloc_destructor);
  return pVal;
}

static PyObject *
deconstruct_p_vpi_value(p_vpi_value v)
{
  PyObject *format, *valu;
  PyObject *tup;
  PyObject *pVal;

  if (debugging) {
    fflush(stdout);
    apvm_msgout("+++ AVPM: In deconstruct_s_vpi_value: %0x\n", v);
  }

  tup = PyTuple_New(2);

  format = PyInt_FromLong(v->format);
  PyTuple_SetItem(tup, 0, format);

  switch (v->format) {
  case 0:
    valu = PyInt_FromLong(99999999); /* marker for no value: Icarus */
    break;

  case vpiBinStrVal:
  case vpiOctStrVal:
  case vpiDecStrVal:
  case vpiHexStrVal:
    valu = PyString_FromString(v->value.str);
    break;
    
  case vpiIntVal:
    valu = PyInt_FromLong(v->value.integer);
    break;

  case vpiRealVal:
    valu = PyFloat_FromDouble(v->value.real);
    break;

  case vpiStringVal:
    valu = PyString_FromString(v->value.str);
    break;

  case vpiSuppressVal:
    valu = PyInt_FromLong(v->value.integer);
    break;

  default:
    fprintf(stderr, "+++APVM: Unknown format: %d\n", v->format);
    PyErr_SetString(apvm_vpi_error, "don't know what in deconstruct_p_vpi_value");
    return NULL;
  };
  PyTuple_SetItem(tup, 1, valu);

  return tup;
}
     

static char deconstruct_s_vpi_value_desc[] =
"unpack_s_vpi_value(s_vpi_value object) -> (int, <value>)\n\
Given a s_vpi_value opaque C object, return a two-tuple\n\
representing the integer value of its 'type' field and a Python value\n\
corrresponding to its value field.";

static PyObject *
deconstruct_s_vpi_value(PyObject *self, PyObject *args)
{
  p_vpi_value v;

  if (((char*) PyCObject_GetDesc(PyTuple_GetItem(args, 0))) != cob_vpi_value_desc) {
    apvm_msgerr("arg to deconstruct_s_value_time is not correct type\n");
    PyErr_SetString(apvm_vpi_error, "arg to deconstruct_s_value_time");
    return NULL;
  }

  v = (p_vpi_value) PyCObject_AsVoidPtr(PyTuple_GetItem(args, 0));

  return deconstruct_p_vpi_value(v);
}


/*
 * Make/deconstruct callback data
 *   Tuple: (reason, callrtn, vpiHandle, p_vpi_time, p_vpi_value, index, userdata)
 */

typedef PLI_INT32 (*cb_rtn_typ) (struct t_cb_data *);
/* the following line is for Icarus */
/* typedef unsigned int (*cb_rtn_typ) (struct t_cb_data *); */

static PyObject *
construct_s_cb_data(PyObject *self, PyObject *args)
{
  PyObject *pValue;

  unsigned int reason;
  cb_rtn_typ cb_rtn;
  vpiHandle systf_h;
  p_vpi_time t;
  p_vpi_value v;
  unsigned int index;
  char *userdata;

  p_cb_data cb;
  cb = (p_cb_data) apvm_malloc(sizeof(s_cb_data));

  reason = PyInt_AsLong(PyTuple_GetItem(args, 0));

  pValue = PyTuple_GetItem(args, 1);
  if (cob_check_typ(pValue, cob_callbackfn_desc)) {
    cb_rtn = (cb_rtn_typ) PyCObject_AsVoidPtr(pValue);
  }
  else {
    PyErr_SetString(apvm_vpi_error, "arg 1 is not cob_callbackfn CObject type");
    return NULL;
  }

  pValue = PyTuple_GetItem(args, 2);
  if (cob_check_typ(pValue, cob_vpiHandle_desc)) {
    systf_h = (vpiHandle) PyCObject_AsVoidPtr(pValue);
  }
  else {
    PyErr_SetString(apvm_vpi_error, "arg 2 is not s_vpiHandle CObject type");
    return NULL;
  }

  pValue = PyTuple_GetItem(args, 3);
  if (cob_check_typ(pValue, cob_vpi_time_desc)) {
    t = (p_vpi_time) PyCObject_AsVoidPtr(pValue);
  }
  else {
    PyErr_SetString(apvm_vpi_error, "arg 3 is not s_vpi_time CObject type");
    return NULL;
  }
    
  pValue = PyTuple_GetItem(args, 4);

  if (pValue == Py_None) {
    v = NULL;
  }
  else if (cob_check_typ(pValue, cob_vpi_value_desc)) {
    v = (p_vpi_value) PyCObject_AsVoidPtr(pValue);
  }
  else {
    PyErr_SetString(apvm_vpi_error, "arg 4 is not s_vpi_value CObject type");
    return NULL;
  }

  index = PyInt_AsLong(PyTuple_GetItem(args, 5));

  userdata = PyString_AsString(PyTuple_GetItem(args, 6));

  cb->reason = reason;
  cb->cb_rtn = cb_rtn;
  cb->obj = systf_h;
  cb->time = t;
  cb->value = v;
  cb->index = index;
  cb->user_data = userdata;

  /* TOM: */
  /* pValue =  PyCObject_FromVoidPtrAndDesc((void*) cb, cob_vpi_cb_data_desc, apvm_malloc_destructor); */
  pValue =  PyCObject_FromVoidPtrAndDesc((void*) cb, cob_vpi_cb_data_desc, NULL);

  return pValue;

}

static PyObject*
deconstruct_p_cb_data(p_cb_data cb)
{
  PyObject *tup, *pVal;

  tup = PyTuple_New(7);

  pVal = PyInt_FromLong(cb->reason);
  PyTuple_SetItem(tup, 0, pVal);

  if (cb->cb_rtn != NULL) {
    pVal = PyCObject_FromVoidPtrAndDesc(cb->cb_rtn, cob_callbackfn_desc, NULL);
  }
  else {
    Py_INCREF(Py_None);
    pVal = Py_None;
  }
  PyTuple_SetItem(tup, 1, pVal);

  if (cb->obj != NULL) {
    pVal = PyCObject_FromVoidPtrAndDesc(cb->obj, cob_vpiHandle_desc, NULL);
  }
  else {
    Py_INCREF(Py_None);
    pVal = Py_None;
  }
  PyTuple_SetItem(tup, 2, pVal);

  if (cb->time != NULL) {
    pVal = PyCObject_FromVoidPtrAndDesc(cb->time, cob_vpi_time_desc, NULL);
  }
  else {
    Py_INCREF(Py_None);
    pVal = Py_None;
  }
  PyTuple_SetItem(tup, 3, pVal);

  if (cb->value != NULL) {
    pVal = PyCObject_FromVoidPtrAndDesc(cb->value, cob_vpi_value_desc, NULL);
  }
  else {
    /* 06/17/2004  */
    Py_INCREF(Py_None);
    pVal = Py_None;
  }
  PyTuple_SetItem(tup, 4, pVal);

  pVal = PyInt_FromLong(cb->index);
  PyTuple_SetItem(tup, 5, pVal);

  pVal = PyString_FromString(cb->user_data);
  PyTuple_SetItem(tup, 6, pVal);

  return tup;
}

static PyObject *
deconstruct_s_cb_data(PyObject *self, PyObject *args)
{
  PyObject *arg;
  p_cb_data v;

  arg = PyTuple_GetItem(args, 0);
  cob_check_typ(arg, cob_vpi_cb_data_desc);

  v = (p_cb_data) PyCObject_AsVoidPtr(arg);
  return deconstruct_p_cb_data(v);
}

  

/*
 * Get the value of an object like an s_vpi_value object.
 */
static PyObject *
get_value_like(PyObject *self, PyObject *args)
{
  vpiHandle     h;
  p_vpi_value   v;
  s_vpi_value   s;

  PyObject *phandle;
  PyObject *pvalue;

  phandle = PyTuple_GetItem(args, 0);
  pvalue = PyTuple_GetItem(args, 1);
    
  h = (vpiHandle) PyCObject_AsVoidPtr(phandle);
  v = (p_vpi_value) PyCObject_AsVoidPtr(pvalue);

  s.format = v->format;
  vpi_get_value(h, &s);
  chkvpierr();

  return deconstruct_p_vpi_value(&s);
}

/*
 * Get the time like an s_vpi_time object.
 */
static PyObject *
get_time_like(PyObject *self, PyObject *args)
{
  vpiHandle     h;
  p_vpi_time    t;
  s_vpi_time    s;

  PyObject *phandle;
  PyObject *ptime;

  phandle = PyTuple_GetItem(args, 0);
  ptime = PyTuple_GetItem(args, 1);
    
  h = (vpiHandle) PyCObject_AsVoidPtr(phandle);
  t = (p_vpi_time) PyCObject_AsVoidPtr(ptime);

  s.type = t->type;
  vpi_get_time(h, &s);
  chkvpierr();

  return deconstruct_p_vpi_time(&s);
}

/*
 * Set the value of an object given a value object.
 */

static char put_value_desc[] =
"put_value(handle, value, timeval/None, delaytype)\n\
\n\
Put a VPI value on a VPI object named by 'handle' with a delay using\n\
the timeval and delaytype.  A timeval of None is translated into the\n\
C value NULL.";


static PyObject *
put_value(PyObject *self, PyObject *args)
{
  PyObject *phandle;
  PyObject *pvalue;
  PyObject *ptimeval;
  PyObject *pdelaytype;

  vpiHandle h;
  p_vpi_value v;
  p_vpi_time t;
  unsigned int d;

  phandle = PyTuple_GetItem(args, 0);
  pvalue = PyTuple_GetItem(args, 1);
  ptimeval = PyTuple_GetItem(args, 2);
  pdelaytype = PyTuple_GetItem(args, 3);
    
  h = (vpiHandle) PyCObject_AsVoidPtr(phandle);
  v = (p_vpi_value) PyCObject_AsVoidPtr(pvalue);
  d = (unsigned int) PyInt_AsLong(pdelaytype);
  

  if (ptimeval == Py_None) {
    vpi_put_value(h, v, NULL, vpiNoDelay);
    chkvpierr();
  }
  else {
    t = (p_vpi_time) PyCObject_AsVoidPtr(ptimeval);
    vpi_put_value(h, v, t, d);
    chkvpierr();
  };

  Py_INCREF(Py_None);
  return Py_None;
}

/*
 * schedule a callback
 *   Arg: cb_data struct
 */
static PyObject *
register_cb(PyObject *self, PyObject *args)
{
  PyObject *arg0;
  p_cb_data cb;
  vpiHandle h;
  PyObject *ph;

  arg0 = PyTuple_GetItem(args, 0);
  cob_check_typ(arg0, cob_vpi_cb_data_desc);

  cb = (p_cb_data) PyCObject_AsVoidPtr(arg0);

  if (debugging) {
    fprintf(stderr, "+++ APVM: before vpi_register_cb\n");
    fprintf(stderr, "+++ CB: %d %0x %0x %0x %0x %0x %0x (%c%c%c%c...)\n",
            cb->reason, cb->cb_rtn, cb->obj, cb->time, cb->value,
            cb->index, cb->user_data,
            cb->user_data[0], cb->user_data[1], cb->user_data[2], cb->user_data[3]);
  }

  h = vpi_register_cb(cb);
  chkvpierr();

  if (debugging) {
    fprintf(stderr, "+++ APVM: after vpi_register_cb: %0x\n", h);
  }

  /* TOM: decide what to do with the handle and whether to free it */

  /* TOM: ran into problems with Icarus which seems to be more strict about
   * how vpi_free_object is used with callback handles.  In short, it seems that
   * calling free on a cb handle cancles the cb.  But called after the callback
   * occurs is an error and causes a segfault.
   */

  /* ph = PyCObject_FromVoidPtrAndDesc(h, cob_vpiHandle_desc, vpihandle_destructor); */
  ph = PyCObject_FromVoidPtrAndDesc(h, cob_vpiHandle_desc, NULL);
    
  return ph;
}

/*
 * handle_by_name("path", vpiHandle scope)
 */

static char handle_by_name_desc[] =
"handle_by_name(pathname, scope)\n\
\n\
Get the VPI handle for 'pathname' in the scope given (a VPI handle).\n\
If scope is None, then use the NULL scope.";

static PyObject *
handle_by_name(PyObject *self, PyObject *args)
{
  PyObject *arg0, *arg1;
  char *name;
  vpiHandle scope;
  vpiHandle h;
  PyObject *ph;

  arg0 = PyTuple_GetItem(args, 0);
  name = PyString_AsString(arg0);

  arg1 = PyTuple_GetItem(args, 1);
  if (arg1 == Py_None) {
    scope = NULL;
  }
  else {
    cob_check_typ(arg1, cob_vpiHandle_desc);
    scope = (vpiHandle) PyCObject_AsVoidPtr(arg1);
  }

  h = vpi_handle_by_name(name, scope);
  chkvpierr();
  ph = PyCObject_FromVoidPtrAndDesc(h, cob_vpiHandle_desc, NULL);
  return ph;
}

/*
 * get property value as a string
 */

static char get_str_desc[] =
"get_str(handle, property)\n\
\n\
Get the string-valued property named from the VPI object indicated by handle.";

static PyObject *
get_str(PyObject *self, PyObject *args)
{
  PyObject *arg0, *arg1;
  unsigned int property;
  vpiHandle h;
  char *s;
  PyObject *ps;

  arg0 = PyTuple_GetItem(args, 0);
  property = PyInt_AsLong(arg0);

  arg1 = PyTuple_GetItem(args, 1);
  if (arg1 == Py_None) {
    h = NULL;
  }
  else {
    cob_check_typ(arg1, cob_vpiHandle_desc);
    h = (vpiHandle) PyCObject_AsVoidPtr(arg1);
  }

  s = vpi_get_str(property, h);
  chkvpierr();

  ps = PyString_FromString(s);
  return ps;
}

/*
 * get property value as an int
 */

static char get_desc[] =
"get_str(handle, property)\n\
\n\
Get the string-valued property named from the VPI object indicated by handle.";

static PyObject *
get(PyObject *self, PyObject *args)
{
  PyObject *arg0, *arg1;
  unsigned int property;
  vpiHandle h;
  unsigned int i;
  PyObject *pi;

  arg0 = PyTuple_GetItem(args, 0);
  property = PyInt_AsLong(arg0);

  arg1 = PyTuple_GetItem(args, 1);
  if (arg1 == Py_None) {
    h = NULL;
  }
  else {
    cob_check_typ(arg1, cob_vpiHandle_desc);
    h = (vpiHandle) PyCObject_AsVoidPtr(arg1);
  }

  i = vpi_get(property, h);
  chkvpierr();

  pi = PyInt_FromLong(i);
  return pi;
}

/*
 * get iterator handle
 */
static char iterate_desc[] =
"Get iterator handle.";

static PyObject *
iterate(PyObject *self, PyObject *args)
{
  PyObject *arg0, *arg1;
  unsigned int property;
  vpiHandle h, i;
  PyObject *pi;

  arg0 = PyTuple_GetItem(args, 0);
  property = PyInt_AsLong(arg0);

  arg1 = PyTuple_GetItem(args, 1);
  if (arg1 == Py_None) {
    h = NULL;
  }
  else {
    cob_check_typ(arg1, cob_vpiHandle_desc);
    h = (vpiHandle) PyCObject_AsVoidPtr(arg1);
  }

  i = vpi_iterate(property, h);
  chkvpierr();

  pi = PyCObject_FromVoidPtrAndDesc(i, cob_vpiHandle_desc, NULL);
  return pi;
}

/*
 * scan to next obj in iterator
 */
static char scan_desc[] =
"scan to next obj in iterator.  Return None after last object.";

static PyObject *
scan(PyObject *self, PyObject *args)
{
  PyObject *arg0;
  unsigned int property;
  vpiHandle h, i;
  PyObject *pi;

  arg0 = PyTuple_GetItem(args, 0);
  cob_check_typ(arg0, cob_vpiHandle_desc);
  h = (vpiHandle) PyCObject_AsVoidPtr(arg0);
  i = vpi_scan(h);
  chkvpierr();

  if (i == NULL) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  else {
    pi = PyCObject_FromVoidPtrAndDesc(i, cob_vpiHandle_desc, NULL);
    return pi;
  }
}

/*
 * call free object on handle.  This may not be safe ...
 */

static char free_object_desc[] =
"Free an object handle.";

static PyObject *
free_object(PyObject *self, PyObject *args)
{
  PyObject *arg0;
  unsigned int property;
  vpiHandle h;
  unsigned int i;
  PyObject *pi;

  arg0 = PyTuple_GetItem(args, 0);
  cob_check_typ(arg0, cob_vpiHandle_desc);
  h = (vpiHandle) PyCObject_AsVoidPtr(arg0);

  i = vpi_free_object(h);
  chkvpierr();

  pi = PyInt_FromLong(i);
  return pi;
}

/*
 * call remove_cb on handle.
 */

static char remove_cb_desc[] =
"Remove a registered VPI callback given its handle.";

static PyObject *
remove_cb(PyObject *self, PyObject *args)
{
  PyObject *arg0;
  unsigned int property;
  vpiHandle h;
  unsigned int i;
  PyObject *pi;

  arg0 = PyTuple_GetItem(args, 0);
  cob_check_typ(arg0, cob_vpiHandle_desc);
  h = (vpiHandle) PyCObject_AsVoidPtr(arg0);

  i = vpi_remove_cb(h);
  chkvpierr();

  pi = PyInt_FromLong(i);
  return pi;
}

/*
 * Call vpi_control function.
 */

#if APVM_HAS_VPI_CONTROL

static char control_desc[] = 
"control(operation)\n\
\n\
valid operations:\n\
vpiStop   - execute simulator's $stop\n\
vpiFinish - execute simulator's $finish\n\
vpiReset  - execute simulator's $reset\n";

static PyObject *
control(PyObject *self, PyObject *args)
{
  PyObject *arg0;
  unsigned int val;
  unsigned int i;
  PyObject *pi;

  arg0 = PyTuple_GetItem(args, 0);
  val = PyInt_AsLong(arg0);

  /*
   * Most verilog impls return a value, Icarus is void.
   * I choose to ignore the ret val for now in the interest
   * of portability and return None.
   */
  vpi_control(val);
  chkvpierr();

  Py_INCREF(Py_None);
  return Py_None;
}
#endif



/*
 * Verilog's call back mechanism gives the user only the user_data
 * field to identify himself.  Thus, implementing a per-instance callback
 * mechanism is difficult.  Instead, we implement a single callback for
 * the entire system.
 *
 * This one is useless, however, so we overload it in Python.
 *
 */

static PyObject *
generic_callback(PyObject *self, PyObject *args)
{
  if (debugging) {
    fprintf(stderr, "+++ APVM: In Generic Callback\n");
  }
  Py_INCREF(Py_None);
  return Py_None;
}

/*
 * Very simple link to vpi_printf
 */
static char py_vpi_printf_desc[] =
"Print the string to the Verilog logfile.";

static PyObject *
py_vpi_printf(PyObject *self, PyObject *args)
{
  PyObject *arg0;
  char *s;

  arg0 = PyTuple_GetItem(args, 0);
  s = PyString_AsString(arg0);
  vpi_printf("%s", s);
  chkvpierr();
  Py_INCREF(Py_None);
  return Py_None;
}



/**
 *
 * According to Stuart Sutherland's Verilog PLI book, most Verilogs
 * have adopted the convention that -f followed by a file name
 * includes additional command line args which are placed in a
 * secondary array of strings.  These args may include further
 * plusargs (and further -f flags, for that matter).
 *
 **/

static PyObject * process_optfile(char **arg)
{

  PyObject *l;
  PyObject *pVal;

  l = PyList_New(0);

  while (*arg != NULL) {

    /*
     * PLI book p. 136 describes convention of '-f' argument
     */
    if (strcmp(*arg, "-f") == 0) {
      pVal = process_optfile((char**) *(arg+1));
      arg++;
    }
    else {
      pVal = PyString_FromString(*arg);
    }
    PyList_Append(l, pVal);
    arg++;
  }
  return l;
}

/*
 *
 * Things to put in our module.  Get simulator info and put it in the dict.
 *
 * Module variable 'sim_info' is a tuple.
 *  [0] - arg count
 *  [1] - verilog args, -f contents interpolated
 *  [2] - simulator product information
 *  [3] - simulator version information
 *
 */

static void
apvm_vpi_startup(PyObject *d)
{
  s_vpi_vlog_info       sim_info;
  PyObject *infotup;	/* tuple representing info struct */
  PyObject *argvtup;	/* tuple representing argv list */
  PyObject *pVal;
  PyObject *cbfn0;
  int i;

  vpi_get_vlog_info(&sim_info);
  chkvpierr();

  infotup = PyTuple_New(4);
  PyTuple_SetItem(infotup, 0, PyInt_FromLong((long) sim_info.argc));

  argvtup = PyList_New(0);
  for (i = 0; i < sim_info.argc; i++) {
    if (strcmp(sim_info.argv[i], "-f") == 0) {
      pVal = process_optfile((char**) sim_info.argv[i+1]);
      i++;
    }
    else {
      pVal = PyString_FromString(sim_info.argv[i]);
    }
    PyList_Append(argvtup, pVal);
  }
  
  
  
  PyTuple_SetItem(infotup, 1, argvtup);
  

  /* TOM: I probably have a lot of reference counting to brush up on */
  /* I probably need to officially defref the strings, but since */
  /* they're static - it doesn't matter here */
     
  PyTuple_SetItem(infotup, 2, PyString_FromString(sim_info.product));
  PyTuple_SetItem(infotup, 3, PyString_FromString(sim_info.version));

  PyDict_SetItemString(d, "sim_info", infotup);

  /*
   * While each systf instance receives one of these values, there is
   * a single global callback function as well.  This simple one only
   * dispatches to apvm.generic_callback.
   */

  cbfn0 = PyCObject_FromVoidPtrAndDesc((void*) apvm_callback, cob_callbackfn_desc, NULL);
  if (!cbfn0) {
    apvm_msgerr("Cannot create PyCObject for callback function.");
  }
  PyDict_SetItemString(d, "cbfn0", cbfn0);


}

static char module_doc [] =
"This module provides basic definitions of VPI constants and functions.";

static PyMethodDef apvm_vpi_methods[] = {
  {"get_val_bin_str",           get_val_bin_str,        METH_VARARGS, get_val_bin_str_desc},

  {"pack_s_vpi_time",           construct_s_vpi_time,   METH_VARARGS, construct_s_vpi_time_desc},
  {"unpack_s_vpi_time",         deconstruct_s_vpi_time, METH_VARARGS, deconstruct_s_vpi_time_desc},

  {"pack_s_vpi_value",          construct_s_vpi_value,  METH_VARARGS, construct_s_vpi_value_desc},
  {"unpack_s_vpi_value",        deconstruct_s_vpi_value,METH_VARARGS, deconstruct_s_vpi_value_desc},

  {"pack_s_cb_data",            construct_s_cb_data,    METH_VARARGS, "no doc"},
  {"unpack_s_cb_data",          deconstruct_s_cb_data,  METH_VARARGS, "no doc"},

  {"get_value_like",            get_value_like,         METH_VARARGS, "no doc"},
  {"get_time_like",             get_time_like,          METH_VARARGS, "no doc"},
  {"put_value",                 put_value,              METH_VARARGS, put_value_desc},
  {"get_str",                   get_str,                METH_VARARGS, get_str_desc},
  {"get",                       get,                    METH_VARARGS, get_desc},

  {"register_cb",               register_cb,            METH_VARARGS, "no doc"},
  {"handle_by_name",            handle_by_name,         METH_VARARGS, handle_by_name_desc},
  {"vpi_print",                 py_vpi_printf,          METH_VARARGS, py_vpi_printf_desc},

  {"iterate",                   iterate,                METH_VARARGS, iterate_desc},
  {"scan",                      scan,                   METH_VARARGS, scan_desc},
  {"free_object",               free_object,            METH_VARARGS, free_object_desc},
  {"remove_cb",                 remove_cb,              METH_VARARGS, remove_cb_desc},
#if APVM_HAS_VPI_CONTROL
  {"control",                   control,                METH_VARARGS, control_desc},
#endif
  {"generic_callback",          generic_callback,       METH_VARARGS, "no doc"},

  {NULL, NULL}

};


/*
 * Much of VPI comes from the constant #defines in the vpi_user.h
 * file.  Part of the build process for APVM extracts this information
 * from the selected vpi_user.h file and ensures that it becomes part
 * of the _apvm Python module.
 * 
 * This struct is defined to hold the information for each #define
 * identifier.
 * 
 */

typedef struct {
  char	*name;
  int   val;
  int   flags;
  char	*doc;
} vpi_const_def;


static vpi_const_def apvm_vpi_constants[] = {
#include "apvm_vpidefs.h"
  {NULL, 0, 0, NULL}
};


void
initapvm_vpi(void)
{
  PyObject *m, *d, *v;
  vpi_const_def *p;
  
  m = Py_InitModule3(APVM_MODULE_NAME, apvm_vpi_methods, module_doc);
  d = PyModule_GetDict(m);

  /* Add other things to the dict here */
  apvm_vpi_startup(d);

  apvm_vpi_error = PyErr_NewException("apvm_vpi.error", NULL, NULL);
  PyDict_SetItemString(d, "error", apvm_vpi_error);

  /* Add the constant definitions extracted from vpi_user.h */
  p = apvm_vpi_constants;
  while (p->name != NULL) {
    PyDict_SetItemString(d, p->name, PyInt_FromLong((long)p->val));
    /* p->doc is documentation string, no use for it right now
     */
    p++;
  }

  if (debugging) {
    fprintf(stderr, "+++ APVM: end of initapvm_vpi\n");
  }

}
  

 
 
