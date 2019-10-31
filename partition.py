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

from random import randrange
from bisect import bisect
import types
from re import split

from postscript import *
from segment import Segment
from Modules.Cpartition import *
from parti_simp import *
import sequence
import types
import matrice

import sys
import time

class Partition:
    "Partition"

    def __init__(self, **kw):
        """Keyword argument:
fic -- Build from filename fic.
"""
        self.__tab=[]
        self.__val=0
        self.__name=""
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])
        elif kw.has_key('str'):
            self.read_str(kw['str'])

    def read_nf(self,nf):
        "Build from filename nf."
        try:
            f = open(nf,'rU')
        except(IOError, e):
            print("Unknown file:", nf)
        else:
            s=f.readline()
            f.close()
            self.read_str(s)

            
    def read_str(self, st):
        "Build from  string st. Return True iff ok."
        ch=split(r'XXX|--->',st)
        self.__init__()
        if st.find("--->") != -1:
            f=1
            self.__val=float(ch[len(ch)-1])
        else:
            f=0
            self.__val=0

        if len(ch)>=f+1:
            for i in range(len(ch)-f):
                s=Segment()
                if s.read_str(ch[i]):
                    self.__tab.append(s)
        return 1
        
    def read_Matrice(self, m, **kw):
        """Build from Matrice m, keeping at each position the
descriptor number that is selected by a function. A segment is made
for each run of identical descriptors numbers.
The value of the each segment is the prediction of its descriptor.

Keyword argument:
func -- function func has two arguments, a Matrice and a position, and
        returns a tuple "descriptor number, floating point value"
        (default: returns the tuple best descriptor,best value  (the first
           of the bests descriptors is returned if there are several bests)).
"""

        if kw.has_key('func'):
            f=kw['func']
        else:
            def f(m,i):
                d=m.line(i)
                mx=max(d.values())
                for j in d:
                    if mx==d[j]:
                        return j,mx
                    
        self.__init__()
        l=len(m)
        deb=0
        x,v=f(m,0)
        i=1
        while i<l:
            y,w=f(m,i)
            if x!=y:
                if len(self.__tab)!=0:
                  self.__tab[-1].g_val(v)
                
                if len(x)==1:
                    num=ord(x)
                else:
                    num=int(x[1:])
                v=w
                self.__tab.append(Segment(deb=deb,fin=i-1,num=[num],val=v))
                x=y
                deb=i
            else:
                v+=w
            i+=1
            
        if len(x)==1:
            num=ord(x)
        else:
            num=int(x[1:])
        self.__tab.append(Segment(deb=deb,fin=i-1,num=[num],val=v))
        self.__val=sum([s.val() for s in self.__tab])

    def s_name(self,s):
        "Set its name to string of s"
        self.__name=str(s)
        
    def group(self, lst):
        """Return a Partition by clustering Segments using the numbers
of their descriptors. These numbers are in the list of lists lst. For
example, if l=[[1,2],[3,4]], numbers 1 and 2 are grouped, as well 3
and 4. Other Segments are not changed. Descriptors are lost.
"""
        p=Partition()
        p.__val=self.__val
        l=len(self)
        i=0
        while i<l:
            ll=lst[:]
            sp=self[i]
            s=Segment(deb=sp.deb(),fin=sp.fin(),num=sp.num())
            p.__tab.append(s)
            ll=p.__inclus(s.num(),ll)
            i+=1
            while i<l:
                sp=self[i]
                ll=p.__inclus(sp.num(),ll)
                if ll==[]:
                    break
                else:
                    i+=1
                    s.g_fin(sp.fin())
                    s.g_num(p.__union(s.num(),sp.num()))
        return p


    def build_random(self, lg, np, **kw):
        """Build a random (uniform distribution) np-partition on
data-length lg.

Keyword argument:
ec - minimum length of the segments, at most lg/(np+1) (default: 1).
"""
        self.__init__()
        if kw.has_key("ec"):
            ec=kw["ec"]
            if ec > lg/(np+1):
                return
        else:
            ec=0

        if lg<=0 or np<=0 or np>=lg:
            return
        lv=[lg-1]
        i=0
        while i<np-1:
            x=randrange(0,lg-1)
            posx=bisect(lv,x)
            if (((posx==0) or x-lv[posx-1]>=ec) \
                and ((posx==i or lv[posx]-x>=ec)) \
                and x>=ec-1):
                lv.insert(posx,x)
                i+=1
        i=0
        for j in lv:
            self.__tab.append(Segment(deb=i,fin=j))
            i=j+1

    def __iadd__(self, s):
        """Append Segment $1 at the end of the Partition
(x.__iadd__(s) <==> x+=s).
"""
        if not isinstance(s, Segment):
            print("Bad argument of ", type(s))
        elif s.deb()!=self.len_don():
            print("Bad segment, should begin at position ", self.len_don())
        else:
            self.__tab.append(s)
            self.__val+=s.val()
        return self
    
    def copy(self):
        "Return a NEW copy of the Partition."
        p=Partition()
        for s in self.__tab:
            p.__tab.append(s.copy())
            p.__val=self.__val
            p.__name=self.__name
            return p
                                                                    
###############################################
##### calculs
    
    def viterbi(self, g, l, **kw):
        """Compute the Partition with Lexique l, using Viterbi
algorithm, on sequence g.

Keyword argument:
maxseg - limits the maximum number of segments allowed in the partition to
maxseg (default: 10000). If equals 0, there is no limit to this number.
"""
        maxseg=kw.get("maxseg",10000)
        
        if l.is_empty():
            return
        self.__init__()
        p=Cpartition()
        if isinstance(g, sequence._Seq):
            p.viterbi(g._Seq__c_elem(),l._Lexique__c_elem(),maxseg)
        elif isinstance(g, matrice._Matr):
            p.viterbi(g._Matr__c_elem(),l._Lexique__c_elem(),maxseg)
        else:
            return
        
        self.read_str(str(p))

    def mpp(self, g, l, i):
        """Compute a maximal predictive i-partition on data g, with
Lexique l.
"""
        if l.is_empty():
            return
        p=Parti_simp()
        p.mpp(g,l,i)
        self.read_str(str(p[min(i,len(p))-1]))
        
    def prediction(self, g, l):
        """Compute the prediction on data g of Lexique l with one best
descriptor per segment.
"""
        if l.is_empty():
            return
        x=0
        for s in self.__tab:
            x+=l.prediction(g,deb=s.deb(),fin=s.fin())
        return x
        
    def pts_comm(self, p):
        """Return the number of predictions similar with Partition p.
Returns -1 if data-lengths are different. Predictors' numbers are only
taken into account.
"""

        if self.len_don()!=p.len_don():
            return -1
        res=0
        iseg2=0
        seg2=p[iseg2]
        dseg2=seg2.deb()
        fseg2=seg2.fin()
        nseg2=seg2.num()
        i2=0
        for seg1 in self.__tab:
            nseg1=seg1.num()
            dseg1=seg1.deb()
            fseg1=seg1.fin()
            i1=0
            if nseg1!=[]:
                pos=dseg1
                while pos<=fseg1:
                    while pos > fseg2 or pos < dseg2:
                        iseg2+=1
                        if iseg2>=len(p):
                            pos=fseg1
                            nseg2=[]
                            break
                        seg2=p[iseg2]
                        dseg2=seg2.deb()
                        fseg2=seg2.fin()
                        nseg2=seg2.num()
                        i2=0
                    if nseg2!=[]:
                        if nseg1[i1]==nseg2[i2]:
                            res+=1
                    pos+=1
                    if i1==len(nseg1)-1:
                        i1=0
                    else:
                        i1+=1
                    if i2==len(nseg2)-1:
                        i2=0
                    else:
                        i2+=1
        return res
               
###########################################"
### donnees
        
    def val(self):
        "Return the value."
        return self.__val

    def name(self):
        "Return the name"
        return self.__name
    
    def len_don(self):
        "Return the data-length."
        if len(self.__tab)==0:
            return 0
        else:
            return(self[-1].fin()+1)

    def __getitem__(self,i):
        "Return Segment i (x.__getitem__(i) <==> x[i])."
        return self.__tab[i]

    def num(self):
        "Return the list of descriptors' numbers."
        l=[]
        for s in self:
            for n in s.num():
                if not n in l:
                    l.append(n)
        return l

############################################
###   sorties

    def __str__(self):
        """(x.__str__()<==> str(x))."""
        st=""
        if len(self.__tab)==0:
            return st
        for i in range(len(self.__tab)-1):
            st+= str(self.__tab[i]) +" XXX "
        st+=str(self.__tab[len(self.__tab)-1])+" ---> "
        st+="%.12g" %self.__val
        return st

    def __len__(self):
        "Return the number of Segments (x.__len__() <==> len(x))."
        return len(self.__tab)
    
    def abr(self):
        "Return the string without the descriptors."
        st=""
        if len(self.__tab)==0:
            return st
        for i in range(len(self.__tab)-1):
            st+= self.__tab[i].abr() +" XXX "
        st+=self.__tab[len(self.__tab)-1].abr() +" ---> "
        st+="%.12g" %self.__val
        return st

        
    def draw_nf(self, nf, **kw):
        """Draw with postscript language in file of name nf.

Keyword arguments:
seg -- draw only the segments which descriptors have their number in
       the list seg;
num -- if equals 1, numbers of the descriptors are written;
func -- the height of each arc is proportional to value of function
        func computed on each Segment s.
"""
        try:
            f=open(nf,'w')
        except(IOError, e):
            print("Probleme ouverture: ", nf)
        else:
            if kw.has_key('seg') and type(kw['seg'])==types.ListType:
                lnum=kw['seg']
                lseg=[]
                for s in self.__tab:
                    for x in s.num():
                        if x in lnum:
                            lseg.append(s)
                            break
            else:
                lseg=self.__tab
                
            num=kw.get('num',0)
            
            func=kw.get('func',lambda x:1)

            lval=map(func,lseg)
            if lval==[]:
                f.close()
                return
            
            maxval=max(lval)
            minval=min(lval)

            if maxval==minval:
                minval-=1
                maxval+=0.1
            else:
                marge=0.1*(maxval-minval)
                minval-=marge
                maxval+=marge

            if maxval*minval<0:
                debval=0
            elif maxval <0:
                debval=maxval
            else:
                debval=minval
                
            marge=0.1*(maxval-minval)
                
            c=Cadre(0,minval,self.len_don(),maxval)
            c.prep_ps(f)
            c.abscisses(f)
            c.ordonnees(f)
            f.write(SETLINEWIDTH(1))
            for i in range(len(lseg)):
                s=lseg[i]
                v=lval[i]
                deb=s.deb()-0.2
                fin=s.fin()+0.2
                f.write(MOVE_TO(deb, debval))
                f.write(CURVE_TO(deb, v, deb, v, (deb+fin)/2, v))
                f.write(MOVE_TO(fin, debval))                
                f.write(CURVE_TO(fin, v, fin, v,(deb+fin)/2, v))
                if num and s.num() is not None:
                    st=str(s.num())
                    f.write(TEXT_CENTER(0.5*(fin+deb), v+(marge/10), st[1:-1]))
                
            f.write(TEXT_DROIT(-0.01*self.len_don(),(maxval+minval)/2,self.__name))
            f.write(STROKE())
            f.close()

    def __draw(self, f, pos, lnum, num, func):
        """Draw with postscript langage in file f at position pos.
lnum is the list of the descriptors' numbers that filters which
Segments are drawn. If lnum=[], all Segments are drawn.
If num is 1, predictors' numbers are written.
func is the lambda-function of the height of the arcs."""

        if lnum!=[]:
            lseg=[]
            for s in self.__tab:
                for x in s.num():
                    if x in lnum:
                        lseg.append(s)
                        break
        else:
            lseg=self.__tab

        lval=map(func,lseg)
        
        if lval!=[]:
            maxval=max(lval)
            minval=min(lval)
        else:
            maxval=0
            minval=0

        if maxval==minval:
            minval-=1
            maxval+=0.1
        else:
            minval-=0.1*(maxval-minval)
            maxval+=0.1*(maxval-minval)
            
        ec=float(maxval-minval)
        lval=map(lambda x: (x-minval)/ec,lval)

        f.write(NEWPATH())
        f.write(SETLINEWIDTH(1))
        for i in range(len(lseg)):
            s=lseg[i]
            v=lval[i]
            deb=s.deb()-0.2
            fin=s.fin()+0.2
            f.write(MOVE_TO(deb, pos))
            f.write(CURVE_TO(deb, pos+v, deb, pos+v, (deb+fin)/2, pos+v))
            f.write(MOVE_TO(fin, pos))                
            f.write(CURVE_TO(fin, pos+v, fin, pos+v,(deb+fin)/2, pos+v))
            if num and s.num() is not None:
                st=str(s.num())
                f.write(TEXT_CENTER(0.5*(fin+deb), pos+v+0.01, st[1:-1]))

        f.write(TEXT_DROIT(-0.01*self.len_don(),pos+(maxval-minval)/2/ec,self.__name))
        f.write(STROKE())
 
        
########################################
#### Fonctions privees

    def __inclus(self,l1, ll2):
        """$1 liste et $2 liste de listes.
        Retourne la liste des listes qui contiennent tous les elements de l1."""
        ll=[]
        for l in ll2:
            t=1
            for i in l1:
                if not i in l:
                    t=0
                    break
            if t==1:
                ll.append(l)
        return ll
    
    def __union(self, l1, l2):
        "retourne la liste qui a l'ensemble des elements de $1 et $2"
        l=l1[:]
        for i in l2:
            if not i in l:
                l.append(i)
        return l
