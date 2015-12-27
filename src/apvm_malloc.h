/*
 *
 * The definitions in this file are the memory allocation functions
 * used by APVM code.  While the current implementation is only just
 * a macro replacement, if, for some reason, we wanted to substitute
 * a different memory manager, this approach makes it easier.
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

#ifndef _APVM_MALLOC_H_
#define _APVM_MALLOC_H_

#include <string.h>  /* to get decl for strdup */

#define apvm_malloc(x)    malloc(x)
#define apvm_free(x)      free(x)
#define apvm_strdup(x)    strdup(x)


#endif /* _APVM_MALLOC_H_ */

