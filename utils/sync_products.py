#!/usr/bin/python
#from __future__ import unicode_literals
import os
import re

from csv      import DictReader
from roundup  import instance
from optparse import OptionParser

splitre = re.compile (r'[ +_/&-]+')

def normalize_name (name) :
    """ Normalize a name from different case etc.
        We assume unicode input.
    >>> print normalize_name ('Projects + Other')
    PROJECTS-OTHER
    >>> print normalize_name ('  Projects + Other  ')
    PROJECTS-OTHER
    >>> print normalize_name ('PROJECTS-OTHER')
    PROJECTS-OTHER
    >>> print normalize_name ('PROJECTS+OTHER')
    PROJECTS-OTHER
    >>> print normalize_name ('PROJECTS-OTHERS')
    PROJECTS-OTHER
    >>> print normalize_name ('Other')
    OTHER
    >>> print normalize_name ('Others')
    OTHER
    >>> print normalize_name ('OTHERS')
    OTHER
    >>> print normalize_name ('Customized Kits')
    CUSTOMIZED-KITS
    >>> print normalize_name ('CUSTOMIZED-KITS')
    CUSTOMIZED-KITS
    >>> print normalize_name ('EV / Hybrid Vehicle ECU')
    EV-HYBRID-VEHICLE-ECU
    >>> print normalize_name (' EV / Hybrid Vehicle ECU ')
    EV-HYBRID-VEHICLE-ECU
    >>> print normalize_name (' APC&RD')
    APC-RD
    """
    x = '-'.join (l for l in splitre.split (name.upper ()) if l)
    if x == 'OTHERS' :
        x = 'OTHER'
    if x == 'PROJECTS-OTHERS' :
        x = 'PROJECTS-OTHER'
    return x
# end def normalize_name

class Product_Sync (object) :

    levels  = \
        { 'Product Line'     : 1
        , 'Product Use Case' : 2
        , 'Product Family'   : 3
        }

    def __init__ (self, opt, args) :
        self.opt      = opt
        self.args     = args
        tracker       = instance.open (opt.dir)
        self.db       = db = tracker.open ('admin')
        self.prodcats = {}
        self.prodused = {}
        for id in db.prodcat.getnodeids (retired = False) :
            pd  = db.prodcat.getnode (id)
            nn  = normalize_name (pd.name.decode ('utf-8'))
            key = (nn, int (pd.level))
            self.prodused [key] = False
            self.prodcats [key] = pd.id

        self.bu_s     = {}
        self.bu_used  = {}
        for id in db.business_unit.getnodeids (retired = False) :
            bu  = db.business_unit.getnode (id)
            key = normalize_name (bu.name.decode ('utf-8'))
            self.bu_used [key] = False
            self.bu_s    [key] = bu.id

        self.products  = {}
        self.pr_used   = {}
        for id in db.product.getnodeids (retired = False) :
            pr  = db.product.getnode (id)
            key = normalize_name (pr.name.decode ('utf-8'))
            self.pr_used  [key] = False
            self.products [key] = pr.id
    # end def __init__

    def sync (self) :
        dr = DictReader \
            (open (self.args [0], 'r'), delimiter = self.opt.delimiter)

        skey = lambda x : x [1]
        for rec in dr :
            pcats = []
            for k, lvl in sorted (self.levels.iteritems (), key = skey) :
                v = rec [k].strip ().decode (self.opt.encoding)
                if not v or v == '0' or v == '1' :
                    break
                key = (normalize_name (v), lvl)
                par = dict \
                    ( name   = v.encode ('utf-8')
                    , level  = lvl
                    , valid  = True
                    )
                r = self.update_table \
                    (self.db.prodcat, self.prodcats, self.prodused, key, par)
                pcats.append (r)

            v   = rec ['BU Owner'].decode (self.opt.encoding)
            sbu = rec ['Selling BU'].decode (self.opt.encoding)
            if sbu == u'0' or sbu == u'ALL-BUSINESS-UNITS' :
                sbu = []
            else :
                sbu = sbu.split ('+')
                sbu = [normalize_name (x) for x in sbu]
            key = normalize_name (v)
            par = dict (name = v.encode ('utf-8'), valid = True)
            bu  = None
            if v and v != 'ALL-BUSINESS-UNITS' and v != '0' :
                bu  = self.update_table \
                    (self.db.business_unit, self.bu_s, self.bu_used, key, par)

            v   = rec ['Artikelnummer'].decode (self.opt.encoding)
            d   = rec ['Artikelbeschreibung'].decode (self.opt.encoding)
            if bu and sbu and key not in sbu :
                if self.opt.verbose :
                    print "Skipping %s Not owning BU: %s (%s)" % (v, sbu, key)
                continue
            key = normalize_name (v)
            if v and v != '0' and len (pcats) == 3 :
                par = dict \
                    ( name             = v.encode ('utf-8')
                    , description      = d.encode ('utf-8')
                    , business_unit    = bu
                    , is_series        = False
                    , valid            = True
                    , product_family   = pcats [2]
                    , product_use_case = pcats [1]
                    , product_line     = pcats [0]
                    )
                p = self.update_table \
                    (self.db.product, self.products, self.pr_used, key, par)
        self.validity (self.db.prodcat,       self.prodcats, self.prodused)
        self.validity (self.db.business_unit, self.bu_s,     self.bu_used)
        self.validity (self.db.product,       self.products, self.pr_used)
        if self.opt.update :
            self.db.commit()
    # end def sync

    def update_table (self, cls, nodedict, usedict, key, params) :
        if key in nodedict :
            # Update name on first match if we have a new spelling
            if not usedict [key] :
                node = cls.getnode (nodedict [key])
                d = {}
                if node.name != params ['name'] :
                    d ['name'] = params ['name']
                if 'parent' in params and node.parent != params ['parent'] :
                    d ['parent'] = params ['parent']
                if 'prodcat' in params and node.prodcat != params ['prodcat'] :
                    d ['prodcat'] = params ['prodcat']
                for a in 'product_family', 'product_line', 'product_use_case' :
                    if a in params and getattr (node, a) != params [a] :
                        d [a] = params [a]
                bu = 'business_unit'
                if bu in params and node.business_unit != params [bu] :
                    d [bu] = params [bu]
                if d :
                    cls.set (nodedict [key], ** d)
                    if self.opt.verbose :
                        print "Update %s: %s: %s" % (cls.classname, key, d)
        else :
            id = cls.create (** params)
            if self.opt.verbose :
                print "Create %s: %s: %s" % (cls.classname, key, params)
            nodedict [key] = id
        usedict [key] = True
        return nodedict [key]
    # end def update_table

    def validity (self, cls, nodedict, usedict) :
        for k, v in usedict.iteritems () :
            id = nodedict [k]
            if not v and self.opt.verbose :
                print "Invalidating %s: %s" % (cls.classname, k)
            cls.set (id, valid = v)
    # end def validity

# end class Product_Sync

def main () :
    dir     = os.getcwd ()

    cmd = OptionParser ("Usage: %prog [options] inputfile")
    cmd.add_option \
        ( '-d', '--directory'
        , dest    = 'dir'
        , help    = 'Tracker instance directory'
        , default = dir
        )
    cmd.add_option \
        ( '-D', '--Delimiter'
        , dest    = 'delimiter'
        , help    = 'CSV delimiter'
        , default = '\t'
        )
    cmd.add_option \
        ( '-E', '--Encoding'
        , dest    = 'encoding'
        , help    = 'CSV character encoding'
        , default = 'utf-8'
        )
    cmd.add_option \
        ( '-u', '--update'
        , dest   = 'update'
        , help   = 'Really do synchronisation'
        , action = 'store_true'
        )
    cmd.add_option \
        ( '-v', '--verbose'
        , dest   = 'verbose'
        , help   = 'Verbose output'
        , action = 'store_true'
        )
    opt, args = cmd.parse_args ()
    if len (args) != 1 :
        cmd.error ('Need input file')
        sys.exit  (23)

    ps = Product_Sync (opt, args)
    ps.sync ()

if __name__ == '__main__' :
    import codecs
    import locale
    import sys
    sys.stdout = codecs.getwriter (locale.getpreferredencoding ())(sys.stdout)
    main ()