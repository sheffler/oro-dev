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

#ifndef _APVM_MSG_H_
#define _APVM_MSG_H_

int apvm_msgout(char *fmt, ...); /* message to stdout/vpi */
int apvm_msgerr(char *fmt, ...); /* message to stderr/vpi */

#endif  /* _APVM_MSG_H_ */
