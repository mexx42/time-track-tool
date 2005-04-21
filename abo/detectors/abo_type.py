# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004 Ralf Schlatterbeck. All rights reserved
# Reichergasse 131, A-3411 Weidling
# ****************************************************************************
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# ****************************************************************************

Reject = ValueError
from roundup.rup_utils import uni, pretty

def check_period (db, cl, nodeid, new_values) :
    period = new_values.get ('period')
    if not period :
        raise Reject, uni('"%s" muss ausgef�llt werden') % pretty ('period')
    if int (period) != period :
        raise Reject, uni('"%s" muss ganzzahlig sein')   % pretty ('period')
# end def check_period

def init (db) :
    db.abo_type.audit ("create", check_period)
    db.abo_type.audit ("set",    check_period)
# end def init
