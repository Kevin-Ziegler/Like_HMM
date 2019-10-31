# Copyright 2005 Laurent GUEGUEN
# 
# This file is part of Sarment.
# 
# Sarment is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# Sarment is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Sarment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import compte
import matrice
import sequence

#doit etre apres les import precedents...
from Modules.Cdesc_comp import *

class Descripteur:
    "Descripteur"

    def __init__(self,n,**kw):
        """ Construct with number n.

Keyword arguments:
str -- descriptor is string str;
prop -- compute from Proportion prop;
fic -- build from first line of filename fic;
prop -- build from Lproportion file of name fprop;
default -- as read from string "".
"""
        self.__desc=Cdesc_comp()
        self.__num=n
        if kw.has_key("str"):
            self.read_str(kw["str"])
        elif kw.has_key("prop"):
            self.read_prop(kw["prop"])
        elif kw.has_key("fic"):
            try:
                f = open(kw["fic"],'rU')
            except IOError, e:
                print "Unknown file: ", kw["fic"]
                return
            self.read_str(f.readline())
            f.close()
        elif kw.has_key("fprop"):
            p=compte.Proportion(fic=kw['fprop'])
            self.read_prop(p)
            del p

    def read_str(self, st):
        """ Build from string st. Iff not ok, is emptied.
"""
        self.__desc.read_str(st,self.__num)

    def read_prop(self, p):
        """Build from Proportion p. Compute automatically
log-probabilites, or -10000 if log not possible.
"""
        self.read_str(p._Proportion__str_loglex())

    def copy(self,i):
        "Return a NEW copy Descripteur of the Descripteur, with number i."
        d=Descripteur(i)
        d.__desc.equals(self.__desc)
        return d

    def equals(self, x):
        "Become a copy of Descripteur x, keeping its own number."
        self.__desc.equals(self.__desc)

    def prediction(self, d, i):
        "Return the prediction on data D at position i."
        if isinstance(d, matrice._Matr):
            return self.__desc.pred(d._Matr__c_elem(),i)
        elif isinstance(d, sequence._Seq):
            return self.__desc.pred(d._Seq__c_elem(),i)

######################################################
### sorties
    
    def __str__(self):
        """(x.__str__()<==> str(x))"""
        return str(self.__desc)

    def num(self):
        "Return the number of the Descripteur."
        return self.__num
        


