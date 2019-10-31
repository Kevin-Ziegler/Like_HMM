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

class Segment:
    "Segment in a Partition"

    def __init__(self,**kw):
        """ constructor.

Keyword arguments:
deb -- begin position is deb (default: 0);
fin -- end position is fin (default: 0);
num -- descriptor number is a copy of list num (default: []);
dsc -- descriptor is string dsc (default: "");
val -- (prediction) value is val (default:0).
"""
        
        self.__pos_d=kw.get("deb",0)
        self.__pos_f=kw.get("fin",0)
        self.__dsc=kw.get("dsc","")
        self.__num=kw.get("num",[])[:]
        self.__val=kw.get("val",0)
        
    def read_str(self, st):
        "Build from string st. Return True iff ok."
        pat='\s*<(?P<deb>\d+)-(?P<fin>\d+)>(?P<num>[0-9,]*):(?P<val>[-+\.e\d]*):(?P<mot>\S*)\s*'
        r=re.compile(pat)
        g=r.match(st)
        if g:
            self.__pos_d=eval(g.group('deb'))
            self.__pos_f=eval(g.group('fin'))
            s=g.group('val')
            if s!="":
                self.__val=float(s)
            s=g.group('num')
            if s!="":
                ch=re.split(r',',s)
                self.__num=[]
                for n in ch:
                    self.__num.append(int(n))
            self.__dsc=g.group('mot')
            return 1
        else:
            return 0

    def g_deb(self,i):
        "Beginning position is i"
        self.__pos_d=i

    def g_fin(self,i):
        "Ending position is i"
        self.__pos_f=i

    def g_num(self,l):
        "List numbers of the segment is l"
        self.__num=l

    def g_dsc(self,m):
        "The string of the descriptor of the segment is m"
        self.__dsc=m
        
    def g_val(self, v):
        "Value is v"
        self.__val=v
        
##################################
### donnees
        
    def deb(self):
        "Return beginning position"
        return self.__pos_d

    def fin(self):
        "Return ending position"
        return self.__pos_f

    def num(self):
        "Return the list of descripors' numbers"
        return self.__num

    def dsc(self):
        "Return the string of the descriptor"
        return self.__dsc

    def val(self):
        "Return the value"
        return self.__val
    
    def __len__(self):
        return self.__pos_f-self.__pos_d+1

    def copy(self):
        "Return a copy of the Segment."
        return Segment(deb=self.deb(),fin=self.fin(),num=self.num(), mot=self.word(),
                  val=self.val())

##################################
#### sortie
        
    def __str__(self):
        """ (x.__str__()<==> str(x))"""
        s= "<%d-%d>" %(self.__pos_d,self.__pos_f)
        if self.__num!=[]:
            l=len(self.__num)
            s+="%d" %(self.__num[0])
            i = 1
            while i < l:
                s+=",%d" %(self.__num[i])
                i+=1
        s+=":"
        if self.val()!=0:
            s+="%.12g" %(self.__val)
        s+=":%s" %(self.__dsc)
        return s
    
    def abr(self):
        "Return the string without the descriptor."
        s= "<%d-%d>" %(self.__pos_d,self.__pos_f)
        if self.__num!=[]:
            l=len(self.__num)
            s+="%d" %(self.__num[0])
            i = 1
            while i < l:
                s+=",%d" %(self.__num[i])
                i+=1
        s+=":"
        s+="%.12g" %(self.__val)
        s+=":"
        return s
    
