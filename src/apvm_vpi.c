/** -*- indent-tabs-mode: nil -*-
 *
 * This is the function that should be added to the
 * global vlog_starupt_routines[] array.
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
 **/


void apvm_startup()
{
  vpi_printf("*** Registering APVM PLI functions.\n");
  apvm_register();
}

/**
 *
 * Required structure for initializing VPI routines for MTI simulator.
 *   Note: apparently on AIX a file called "x.exports" is necessary
 *   for the linker to "export" this array.  See the MTI examples/vpi
 *   directory for an example.
 *
 * I think that on Sun and HP, MTI simply assumes that this symbol
 * exists and uses it to load the functions.
 *
 **/

extern void (*vlog_startup_routines[])() = {
    apvm_startup,
    0
};

