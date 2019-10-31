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

import re
import types

from postscript import *
import partition 
from Modules.Cparti_simp import *
import sequence
import matrice

class Parti_simp:
    "Simple partitioning"

    def __init__(self, **kw):
        """Keyword argument:
fic --  build from filename f.
"""
        self.__tab=[]
        self.__valmax=0
        self.__nbmax=0
        if kw.has_key("fic"):
            self.read_nf(kw["fic"])
            
    def read_nf(self, nf):
        """Build from filename nf. If a Partition of the file has no
name, it gets its index in the list as name.
"""
        try:
            f = open(nf,'rU')
        except IOError, e:
            print "Unknown file: ", nf
        else:
            self.__init__()
            s=f.readline()
            while s:
                s.strip()
                if (s.find("MAX",0,3)==0):
                    pat='MAX\((?P<nm>\d*)\)\s*--->\s*(?P<val>-?\d+\.?\d*)'
                    r=re.compile(pat)
                    g=r.match(s)
                    if g:
                        self.__nbmax=eval(g.group('nm'))
                        self.__valmax=float(g.group('val'))
                else:
                    p=partition.Partition()
                    if p.read_str(s):
                        self.__tab.append(p)
                        if p.name()=="":
                            p.s_name(str(len(self.__tab)))
                s=f.readline()
            f.close()

    def build_random(self, lg, np):
        """Build a random (uniform distribution) np-partitioning on
data-length lg.
"""
        if lg<=0 or np<=0 or np>=lg:
            return
        self.__init__()
        for i in range(np):
            p=partition.Partition()
            p.build_random(lg,i+1)
            self.__tab.append(p)

            
########################################################
#### calculs

    def mpp(self, d, l, i):
        """Compute a maximal predictive i-partitioning on data d with
Lexique l. Each new k-Partition gets its length k as name.
"""
        if l.is_empty():
            return
        self.__init__()
        p=Cparti_simp()
        if isinstance(d, matrice._Matr):
            p.lisse(d._Matr__c_elem(),l._Lexique__c_elem(),i)
        elif isinstance(d, sequence._Seq):
            p.lisse(d._Seq__c_elem(),l._Lexique__c_elem(),i)

        j=1
        x=p[j]
        while x!="":
            q=partition.Partition()
            q.read_str(x)
            self.__tab.append(q)
            q.s_name(len(q))
            j+=1
            x=p[j]
        self.__nbmax=p.np_max()
        self.__valmax=p.val_max()

    def prediction(self, d, l):
        """Return the list of predictions on data d and Lexique l on
the partitions.
"""
        lv=[]
        for x in self.__tab:
            lv.append(x.prediction(d,l))
        return lv
    
    def pts_comm(self, ps):
        """Return the number of different predictions with Parti_simp
ps, Partition after Partition.
Return -1 if data-lengths are different.
Predictors' numbers are only taken into account.
"""
        x=0
        for i in range(min(len(self),len(ps))):
            y=self[i].pts_comm(ps[i])
            if y==-1:
                return -1
            else:
                x+=y
        return x


########################################
###  donnees

    def len_don(self):
        "Return data-length."
        if len(self.__tab)==0:
            return 0
        else:
            return self.__tab[0].len_don()

    def __len__(self):
        """(x.__len__() <==> len(x))"""
        return len(self.__tab)
    
    def __getitem__(self, i):
        "(x.__getitem__(i) <==> x[i])"
        return self.__tab[i]

    def __getslice__(self, i, j):
        """Return a Parti_simp made of the selected Partitions.
(x.__getslice__(i,j) <==> x[i:j]).
"""
        ps=Parti_simp()
        ps.__valmax=self.__valmax
        ps.__nbmax=self.__nbmax
        ps.__tab=self.__tab[i:j]
        return ps

    def __delitem__(self,i):
        "(x.__delitem__(i) <==> del x[i])"
        del self.__tab[i]
        
    def __delslice__(self,i,j):
        "(x.__delslice__(i,j) <==> del x[i:j])"
        del self.__tab[i:j]
        
    def append(self, p):
        """Append Partition p to the end of self. Data length of p
must be the same as the one of self. If p has no name, it gets the
length of the Parti_simp as name.
"""
        if len(self)==0 or p.len_don()==self.len_don():
            self.__tab.append(p)
            if p.name()=="":
                p.s_name(str(len(self.__tab)))
        
    def insert(self, i, p):
        """Insert Partition p before index i. Data length of p must be
the same as the one of self. If p has no name, it gets the length of
the Parti_simp as name.
"""
        if p.len_don()==self.len_don():
            self.__tab.insert(i,p)
            if p.name()=="":
                p.s_name(str(len(self.__tab)))
        
    def filter(self, func):
        """Return a Parti_simp made of the Partition for which function
func returns True.
"""
        ps=Parti_simp()
        ps.__valmax=self.__valmax
        ps.__nbmax=self.__nbmax
        ps.__tab=filter(func, self.__tab)
        return ps
        
    def group(self, lst):
        """Return a Parti_simp where the Partition are the result of method
group of Partition class applied on the Partition of self.
"""
        ps=Parti_simp()
        ps.__valmax=self.__valmax
        ps.__nbmax=self.__nbmax
        for i in self.__tab:
            ps.__tab.append(i.group(lst))
        return ps

    def sort(self):
        """The partitions are sorted following their number of segment."""

        def f(x,y):
            if len(x)<len(y):
                return -1
            elif len(x)==len(y):
                return 0
            else:
                return 1
            
        self.__tab.sort(f)
        
    def ls_val(self):
        "Return the list of the successive values."
        l=[]
        for i in range(len(self.__tab)):
            l.append(self[i]._Partition__val)
        return l
        
########################################
##  sorties
    
    def __str__(self):
        """(x.__str__()<==> str(x))"""
        s=""
        for x in self.__tab:
            s+=str(x)
            s+='\n'
        s+="MAX(%d) ---> %.12g\n" %(self.__nbmax, self.__valmax)
        return s


    def abr(self):
        """Return the string of the simple partitioning without the
descriptors.
"""
        s=""
        for x in self.__tab:
            s+=x.abr()
            s+='\n'
        s+="MAX(%d) ---> %.12g\n" %(self.__nbmax, self.__valmax)
        return s

    def draw_nf(self, nf, **kw):
        """Draw with postscript langage in file of name nf.
        
Keyword arguments:
seg -- draw only the segments which descriptors have their number in
       the list seg;
num -- if equals 1, numbers of the descriptors are written;
func -- the height of each arc is proportional to lambda-function
        func(s) computed on each Segment s.
"""
        try:
            f=open(nf,'w')
        except IOError, e:
            print "Problem opening: ", nf
        else:
            if kw.has_key('seg') and type(kw['seg'])==types.ListType:
                lnum=kw['seg']
            else:
                lnum=[]

            num=kw.get('num',0)

            func=kw.get('func',lambda x:1)

            l=len(self.__tab)
            ld=self.len_don()
            c=Cadre(0,0,ld,l)
            c.prep_ps(f)
            c.abscisses(f)
            i=l-1
            while i>=0:
                self.__tab[i]._Partition__draw(f,l-i-1,lnum,num,func)
                i-=1
            f.close()
     
    

        
