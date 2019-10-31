# Copyright 2004 Laurent GUEGUEN
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

from Modules.Cmatrice import *
from Modules.Fmatrice import *

import sequence
import math

class _Matr:
    "Virtual Matrix"

    def __init__(self):
        self.__mat=Fmatrice()
        self.__cat={}
        self.__ldesc=[]
        
    def __c_elem(self):
        "Return C++ object."
        return self.__mat


#########################################
### modifications

    def g_val(self, v, c, i):
        "Put value v at character c line i."
        self.__c_elem().g_val(v,self._Matr__cat[c],i)

    def __add__(self, m):
        """Return a Matrice = self + (Matrice m) if both Matrice fit
(x.__add__(m) <==> x+m)."""

        nv=Matrice()
        if self.__mm_type(m):
            ls=len(self)
            nv.generate(ls,self.desc())
            for i in self.desc():
                for j in range(len(self)):
                    nv.g_val(self.val(i,j)+m.val(i,j),i,j)
        return nv

    def __sub__(self, m):
        """Return a Matrice = self - (Matrice m) if Matrices fit
(x.__sub__(m) <==> x-m)."""
        nv=Matrice()
        if self.__mm_type(m):
            ls=len(self)
            nv.generate(ls,self.desc())
            for i in self.desc():
                for j in range(len(self)):
                    nv.g_val(self.val(i,j)-m.val(i,j),i,j)
        return nv

    def __iadd__(self, m):
        """+= (Matrice m) if Matrices fit (x.__iadd__(m) <==> x+=m)."""
        if self.__mm_type(m):
            ls=len(self)
            for i in self.desc():
                for j in range(ls):
                    self.g_val(self.val(i,j)+m.val(i,j),i,j)
        return self

    def __isub__(self, m):
        """-= (Matrice m) if Matrices fit (x.__isub__(m) <==> x-=m)."""
        if self.__mm_type(m):
            ls=len(self)
            for i in self.desc():
                for j in range(ls):
                    self.g_val(self.val(i,j)-m.val(i,j),i,j)
        return self

    def __imul__(self, x):
        """*= (float x)  (m.__imul__(x) <==> m*=x)."""
        ls=len(self)
        for i in self.desc():
            for j in range(ls):
                self.g_val(self.val(i,j)*x,i,j)
        return self
                                            
    def shuffle(self):
        """Quasi-uniformly randomized using (len*(log(len)+1)/2)
transpositions.
"""
        self.__c_elem().melange()

    def set_proba(self):
        """Normalize so that each line corresponds the logarithms of
a probability distribution.
"""
        self.__c_elem().log_normalise()

    def max(self, i):
        """Return the maximum value on descriptor i."""
        x=self.val(i,0)
        lm=len(self)
        t=1
        while t<lm:
            y=self.val(i,t)
            if x<y:
                x=y
            t+=1
        return x

    def exp(self):
        "Replace all the values by their exponential."
        self.__c_elem().exponentielle()

    def ln(self):
        "Replace all the values by their neperian logarithm."
        self.__c_elem().logarithme()

###########################################
### donnees
        
    def __len__(self):
        "Return length of the Matrice (x.__len__() <==> len(x))."
        return len(self.__c_elem())

    def ndesc(self):
        "Return number of descriptors."
        return self.__c_elem().ndesc()

    def desc(self):
        "Return the list of descriptors."
        return self.__ldesc

    def val(self, c, i):
        "Return the value of character c at line i."
        return self.__c_elem()(self.__cat[c],i)

    def line(self,i):
        """Return a dictionnary {character: value of the character at
line i}.
"""
        d={}
        for c in self.desc():
            d[c]=self.val(c,i)
        return d
    
    def __getslice__(self,i,j):
        """!!! Do NOT create a new Matrice; so destruction of the
original Matrice entails destruction of this result.
(x.__getslice__(i,j) <==> x[i:j])"""
        nv=_Matr()
        nv.__c_elem().recup_rel(self.__c_elem(),i,j)
        nv.__maj()
        return nv

#####################################################""
### sorties
    
    def copy(self):
        "Build a NEW Matrice as a copy of the given one."
        m=Matrice()
        m._Matr__c_elem().copy(self._Matr__c_elem())
        m._Matr__maj()
        return m


    def __str__(self):
        """(x.__str__()<==> str(x))"""
        return str(self.__c_elem())

#################################################
###  prives

    def __mm_type(self,m):
        ls=len(self)
        if ls!=len(m):
            return 0
        lm=m.desc()
        lk=self.desc()
        if len(lm)!=len(lk):
            return  0
        for i in lk:
            if not i in lm:
                return 0
        return 1

    def __maj(self):
        self.__cat={}
        self.__ldesc=[]
        nb=self.ndesc()
        for i in range(nb):
            c=self.__mat.carac(i)
            self.__cat['#'+str(ord(c))]=i
            self.__cat[ord(c)]=i
            if str.isalpha(c):
                self.__cat[c]=i
                self.__ldesc.append(c)
            else:
                self.__ldesc.append('#'+str(ord(c)))


##################################################################
##################################################################
##################################################################

    
class Matrice(_Matr):
    "Matrix"

    def __init__(self, **kw):
        """ Keyword argument:
fic -- Build from filename fic.
"""
        _Matr.__init__(self)
        self._Matr__mat=Cmatrice()
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])        

        
    def read_nf(self,nf):
        "Build from filename nf."
        self._Matr__c_elem().read_nf(nf)
        self._Matr__maj()

    def fb(self, g, lx):
        """Build of data g and Lexique lx, using forward-backward
algorithm, with the logarithm of the computed probabilities.
"""
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().FB(g._Seq__c_elem(),lx._Lexique__c_elem())
        elif isinstance(g, _Matr):
            self._Matr__c_elem().FB(g._Matr__c_elem(),lx._Lexique__c_elem())
            
        self._Matr__maj()

    def forward(self, g, lx):
        """Build of data g and Lexique lx, using forward algorithm,
with the logarithm of the computed probabilities.
"""
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().forward(g._Seq__c_elem(),lx._Lexique__c_elem())
        elif isinstance(g, _Matr):
            self._Matr__c_elem().forward(g._Matr__c_elem(),lx._Lexique__c_elem())
        self._Matr__maj()

    def backward(self, g, lx):
        """Build of data g and Lexique lx, using backward algorithm,
with the logarithm of the computed probabilities.
"""
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().backward(g._Seq__c_elem(),lx._Lexique__c_elem())
        elif isinstance(g, _Matr):
            self._Matr__c_elem().backward(g._Matr__c_elem(),lx._Lexique__c_elem())
        self._Matr__maj()
        
    def prediction(self, g, l):
        """ On Lexique l, build from data g. The descriptors are set
using the descriptor numbers of l, and the values at each position are
computed by the predictions of the corresponding descriptors.

The descriptor patterns are set such as the number of the line
corresponds with the descriptor used in first position.
"""
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().predictions(g._Seq__c_elem(), l._Lexique__c_elem())
        elif isinstance(g, _Matr):
            self._Matr__c_elem().predictions(g._Matr__c_elem(), l._Lexique__c_elem())
        self._Matr__maj()

    def smoothe(self, g, sz=1, st=1, **kw):
        """Build for data g, using sliding windows of size sz(=1),
with steps st(=1).
Keyword argument: f -- if equals 'm', compute the mean value,
otherwise compute the sum.
"""
        c=kw.get('f','o')
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().smoothe(g._Seq__c_elem(),sz,st,c)
        elif isinstance(g, _Matr):
            self._Matr__c_elem().smoothe(g._Matr__c_elem(),sz,st,c)
        self._Matr__maj()

    def derivate(self,g):
        """Build computing the differences (pos_i-pos_(i-1)) on data g."""
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().derive(g._Seq__c_elem())
        elif isinstance(g, _Matr):
            self._Matr__c_elem().derive(g._Matr__c_elem())
        self._Matr__maj()

    def integrate(self,g):
        """Build computing the cumulated sums on data g, ie:
res[i]=\sum_{k=0}^i g[k].
"""
        if isinstance(g, sequence._Seq):
            self._Matr__c_elem().integre(g._Seq__c_elem())
        elif isinstance(g, _Matr):
            self._Matr__c_elem().integre(g._Matr__c_elem())
        self._Matr__maj()
        
    def generate(self, lg, l):
        """Create an empty Matrice, with length lg and descriptor
names and numbers, chars, or #numbers, those of list l.
"""
        s=''
        for d in l:
            if type(d)==int:
                s+=chr(d)
            elif type(d)==str:
                if len(d)!=0:
                    if len(d)==1:
                        s+=d
                    elif d[0]=="#":
                        s+=chr(int(d[1:]))
                    else:
                        print "Error in descriptor: ", d
                        return
        self._Matr__c_elem().genere(lg,s)
        self._Matr__maj()


###########################################
### donnees

    def __getslice__(self,i,j):
        """!!! Do NOT create a new Matrice; so destruction of the
original Matrice entails destruction of this result
(x.__getslice__(i,j) <==> x[i:j]).
"""
        nv=_Matr()
        nv._Matr__c_elem().recup_relC(self._Matr__c_elem(),i,j)
        nv._Matr__maj()
        return nv


# #################################################
# ############################

# class Matrice_iter:

#     def __init__(self,mat,lc):
#         self.__mat=mat
#         self.__lc=lc
#         if self.__lc=="c":
#             self.__ln=self.__mat.n_desc()
#         else:
#             self.__ln=len(m)
            
#         self.__ind=-1

#     def next(self):
#         if self.__ind==self.__ln-1:
#             raise StopIteration
#         else:
#             self.__ind+=1
#             if self.__lc=="c":
#                 return self.__mat[self.__lnum[self.__ind]]


        



