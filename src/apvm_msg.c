/*
 * Message layer (printf) functions for APVM.
 *
 * These exist so that it's easy to retarget APVM C-level code
 * to stdio, or vpi_printf, or other streams if needed.
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
 */

#include "apvm_msg.h"
#include "stdarg.h"
#include "stdio.h"

#define __MAXCHARS 20000

static char charbuf[__MAXCHARS];

apvm_msgout(char *fmt, ...)
{
  
  va_list	args;
  int		chars;

  va_start(args, fmt);

  chars = vsprintf(charbuf, fmt, args);

  if (chars >= __MAXCHARS) {
    fprintf(stderr, "Error. apvm_msg formatting buffer too small.\n");
    exit(1);
  }

  vpi_printf("%s", charbuf);
}

apvm_msgerr(char *fmt, ...)
{
  va_list	args;
  int		chars;

  va_start(args, fmt);

  chars = vsprintf(charbuf, fmt, args);

  if (chars >= __MAXCHARS) {
    fprintf(stderr, "Error. apvm_msg formatting buffer too small.\n");
    exit(1);
  }

  vpi_printf("%s", charbuf);
  fprintf(stderr, "%s", charbuf);
}
  

  
