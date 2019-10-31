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

from sequence import *
import lpartition


class Lsequence(list):
    "List of Sequences"

    def __init__(self, **kw):
        """Keyword argument:
fic -- Build from filename f, in FASTA format.
"""
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])

    def read_nf(self,st):
        "Append a list of Sequence from filename st"
        st.strip()
        if (st.rfind(".seq")==len(st)-4):
            a=Sequence()
            if (a.read_nf(st)):
                self.append(a)
        elif (st.rfind(".fa")==len(st)-3) or st.rfind(".fst")==len(st)-4 or (st.rfind(".fas")==len(st)-4):
            self.__recup_fa(st)
        else:
            print "Bad file: " + st
                  

    def read_Lprop(self, lp, nb, lg, **kw):
        """Append with nb Sequences of length lg created randomly
from Lproportion lp.

Keyword argument:
etat_init -- if etat_init is valid, create only Sequences beginning
with descriptor number etat_init. Return the corresponding Lpartition.
"""

        e=kw.get('etat_init',-1)
        
        lpart=lpartition.Lpartition()
        if nb<=0 or lg<=0:
            return lpart
        
        for i in range(nb):
            g=Sequence()
            p=g.read_Lprop(lp, long=lg, etat_init=e)
            self.append(g)
            lpart.append([g,p])

        return lpart

#####################################################
### donnees
    
    def __str__(self):
        """Return string of the Sequence in FASTA format.
(x.__str__()<==> str(x)).
"""
        st=""
        for g in self:
            st+=g.fasta()
        st+="\n"
        return st


        
####################################
###  attributs prives

    def __recup_fa(self,st):
        "Append with a list of Sequences from fasta filename $1"
        try:
            f=open(st,"rU")
        except IOError, e:
            print "Unknown filename: ", st
        else:
            l=f.readline()
            while l:
                if (l[0]=='>'):
                    s=l[1:].strip()
                    i=f.tell()
                    l=f.readline()
                    j=0
                    while l and (l[0]!='>'):
                        j+=len(l)-l.count(' ')-l.count('\t')-1
                        l=f.readline()
                    a=Sequence()
                    a.g_name(s)
                    a.generate(j)
                    f.seek(i)
                    l=f.readline()
                    j=0
                    while l and (l[0]!='>'):
                        l.strip()
                        for c in l:
                            if c != ' ' and c!='\n':
                                a[j]=c
                                j+=1
                        l=f.readline()
                    self.append(a)
            f.close()
        
            
