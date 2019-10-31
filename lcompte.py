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

import math
import sys
import time

import compte 
import lsequence
import lexique
import partition
import sequence
import matrice

class _Lrac_Arb:
    """Dictionnary of {number of descriptor, count or proportion of
words on the sequences}, and count or proportion of transition between
descriptors.
"""

    def __init__(self):
        self.__tab={}  # dictionary of trees
        self.__pas={}  # counts between descriptors

###########
### donnees
        
    def __getitem__(self, i):
        """Return the count of descriptor i ( x.__getitem__(i) <==> x[i])."""
        
        return self.__tab[i]

    def num(self):
        """Return the list of descriptors' numbers."""
        return self.__tab.keys()

    def lg_max(self):
        """Return the length of the longest word."""
        ml=0
        for c in self.__tab.values():
            l=c.lg_max()
            if ml<l:
                ml=l
        return ml

    def inter(self, a, b):
        """Return the count or proportion of transitions from a to b."""
        return self.__pas.get((a,b),0)

    def g_inter(self, a, b, v):
        """Set the count or proportion of transitions from a to b at value v."""
        if self.__pas.has_key((a,b)):
            self.__pas[(a,b)]=v
        else:
            print "Bad descriptors numbers:",a,b
            

    def __setitem__(self, i, c):
        """Set the Compte or Proportion c to descriptor number i
( x.__setitem__(i,c) <==> x[i]=c ).
"""
        if isinstance(c,compte.Compte) or isinstance(c,compte.Proportion):
            if not self.__tab.has_key(i):
                for s in self.num():
                    self.__pas[(s,i)]=0
                    self.__pas[(i,s)]=0
                self.__pas[(i,i)]=0
            self.__tab[i]=c
            
    def alph(self):
        """Return the list of used letters."""
        l=[]
        for t in self.__tab.values():
            for i in t.alph():
                if not i in l:
                    l.append(i)
        return l

##########
### sorties
        
    def __str__(self):
        """Return the string of within and between descriptors' counts.
(x.__str__()<==> str(x))
"""
        st=""
        for m in self.num():
            st+=str(m)+":\n"+str(self.__tab[m])+"\n"
        for m in self.num():
            for n in self.num():
                st+= str(m)+","+str(n)+"\t"+str(self.__pas[(m,n)])+"\n"
        return st



#############################################################
#################################################################
####  Liste de Compte

        
class Lcompte(_Lrac_Arb):
    """Dictionnary of {descriptor number, Compte made on sequences}."""
    
    def __init__(self, **kw):
        """Keyword argument:
fic -- Build using file of name f.
"""
        _Lrac_Arb.__init__(self)
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])

    def read_Lpart(self, lp, lg, **kw):
        """Count lg-length words from the Lpartition lp.
Keyword argument:
alpha --  counts are restricted to letters of alphabet string.
"""

        st=kw.get("alpha",'')

        self._Lrac_Arb__tab={}
        for [g,p] in lp:
            self.__add_intra_part_don(p,g,lg,st)
            
        self._Lrac_Arb__pas={}
        for a in self.num():
            for b in self.num():
                self._Lrac_Arb__pas[(a,b)]=0

        for [g,p] in lp:
            self.__add_inter_part_don(p)


    def read_nf_seq(self, ls, lg, **kw):
        """Count lg-length words from the list of filenames ls. In
each file are the counted sequences. Count number (n-1) is related to
file number n. Between-descriptors transitions are uniformaly
distributed.

Keyword argument:
alpha --  counts are restricted to letters of alphabet string.
"""
        
        st=kw.get(alpha,'')
        num=len(ls)
        self._Lrac_Arb__tab={}
        m=0
        for nf in ls:
            lge=lsequence.Lsequence()
            lge.read_nf(nf)
            c=compte.Compte()
            self._Lrac_Arb__tab[m]=c
            d=0
            e=0
            for g in lge:
                c.add_seq(g,lg,alpha=st)
                e+=1
            self._Lrac_Arb__pas[(m,m)]=c['.'*lg]
            d=c['.'*(lg-1)]-self._Lrac_Arb__pas[(m,m)]
            if num!=1:
                e=d/(num-1)
                n=0
                if n==m:
                    n+=1
                self._Lrac_Arb__pas[(m,n)]=e+ (d%(num-1))
                n+=1
                while n<num:
                    if n!=m:
                        self._Lrac_Arb__pas[(m,n)]=e
                    n+=1
            print nf + " read "
            m+=1
			

    def read_nf(self, nf):
        """Read a file of several Compte"""
        self.__init__()
        try:
            f = open(nf,'rU')
        except IOError, e:
            print "Unknown filename: ", nf
            return
        s=f.readline()
        while s and s.find(':')==-1:
            s=f.readline()
        if not s:
            print "No descriptor in " + nf
            f.close()
            return

        while s and s.find(',')==-1:
            i=s.find(':')
            if i!=-1:
                try:
                    d=int(s[:i])
                except ValueError, e:
                    print "Bad descriptor in: " + s
                    self.__init__()
                    f.close()
                    return
                tab=self._Lrac_Arb__tab.setdefault(d,compte.Compte())
            else:
                t=s.split()
                if t!=[]:
                    if len(t)<2:
                        print "Problem at line: " + s
                        self.__init__()
                        f.close()
                        return
                    tab._Compte__add(t[0],float(t[1]))
            s=f.readline()

        while s:
            t=s.split()
            if t!=[]:
                tt=t[0].split(',')
                if len(tt)==2:
                    try:
                        self._Lrac_Arb__pas[(int(tt[0]),int(tt[1]))]=float(t[1])
                    except ValueError, e:
                        print "Bad transition in: " + s
                        f.close()
                        return
                else:
                    print "Problem at line " + s
                    f.close()
                    return
            s=f.readline()


        for i in self._Lrac_Arb__tab:
            for j in self._Lrac_Arb__tab:
                self._Lrac_Arb__pas.setdefault((i,j),0)
                
        f.close()

    def add_Partition(self, p, g, lg, **kw):
        """Add a count of words of at most lg-length on Partition p
and Sequence g.

Keyword argument:

alpha -- count only words which letters are in string. If empty
         string, do as if no keyword alpha.
fact -- each word counts fact (default: 1 ).
"""

        st=kw.get('alpha','')
        v=kw.get('fact',1.0)
        
        self.__add_intra_part_don(p,g,lg,st,v)
        
        for a in self.num():
            for b in self.num():
                if not self._Lrac_Arb__pas.has_key((a,b)):
                    self._Lrac_Arb__pas[(a,b)]=0
                    
        self.__add_inter_part_don(p,v)        
        

    def strip(self):
        """Return the Lcompte without characters ^."""
        lc=Lcompte()
        lnum=self.num()
        for d in lnum:
            lc[d]=self[d].strip()

        for a in lnum:
            for b in lnum:
                lc._Lrac_Arb__pas[(a,b)]=self.inter(a,b)

        return lc

    def rstrip(self):
        """Return the Lcompte without ending characters ^."""
        lc=Lcompte()
        lnum=self.num()
        for d in lnum:
            lc[d]=self[d].rstrip()

        for a in lnum:
            for b in lnum:
                lc._Lrac_Arb__pas[(a,b)]=self.inter(a,b)

        return lc
    

#########################################
#### prive

    def __add_intra_part_don(self, p, g, lg, alph='',f=1):
        """Add within counts in Partition p on Sequence g, with
 lg-length words, following alphabet alph, with factor f. Count words
 that END in each segment.
 """
        gf=len(g)-1
        for s in p:
            n=s.num()
            sf=s.fin()
            ln=len(n)
            if ln==0:
                print "No descriptor in ", s
            else:
                r=lg%ln
                if r==ln-1:
                    pd=0
                else:
                    pd=r+1
                for i in range(ln):
                    lci=self._Lrac_Arb__tab.setdefault(n[pd+i],compte.Compte())
                    m=s.deb()-lg+i+1
                    while m<0:
                        if alph!='':
                            m2=m+lg-1
                            while m2>=0 and g[m2] in alph:
                                m2-=1
                            if m2<0:
                                lci._Compte__add_suff(g,0,m+lg-1,f)
                        else:
                            lci._Compte__add_suff(g,0,m+lg-1,f)
                        m+=ln
                        
                    while m<=sf-lg+1:
                        if alph!='':
                            m2=m+lg-1
                            while m2>=m and g[m2] in alph:
                                m2-=1
                            if m2<m:
                                lci._Compte__add_word(g,m,m+lg-1,f)
                        else:
                            lci._Compte__add_word(g,m,m+lg-1,f)
            
                        m+=ln

                    if sf==gf:
                          while m<=sf:
                              if alph!='':
                                  m2=sf
                                  while m2>=m and g[m2] in alph:
                                      m2-=1
                                  if m2<m:
                                      lci._Compte__add_pref(g,m,sf,lg,f)
                              else:
                                  lci._Compte__add_pref(g,m,sf,lg,f)
      
                              m+=ln
                    

    def __add_inter_part_don(self, p, f=1):
        """Add between counts in Partition p with factor f; Number of
descriptors must already exist in the counts.
"""
        m=[]
        for s in p:
            n=s.num()
            ln=len(n)
            if n!=[]:
                if m!=[]:
                    self._Lrac_Arb__pas[(m[r-1],n[0])]+=f
                q=(s.fin()-s.deb()+1) / ln
                r=(s.fin()-s.deb()+1) % ln
                for i in range(-1,ln-1):
                    self._Lrac_Arb__pas[(n[i],n[i+1])]+=q*f
                self._Lrac_Arb__pas[(n[-1],n[0])]-=f
                for i in range(-1,r-1):
                    self._Lrac_Arb__pas[(n[i],n[i+1])]+=f
            m=n


#############################################################
#################################################################
####  Liste de Proportion

class Lproportion(_Lrac_Arb):
    """Dict of {number of descriptor, proportion of words}."""

    def __init__(self, **kw):
        """Opt: if fic=f, builds from filename f."""
        _Lrac_Arb.__init__(self)
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])

    def read_Lcompte(self, lc, **kw):
        """Build from Lcompte lc with options:
        
Keyword argument:
lpost -- posterior (ie on the right) must have as much as possible
         lpost letters (default: > 0).
lprior -- prior (ie on the left) msut have at most lprior letters (default: 0).
"""
        nlc=lc.num()
        for d in nlc:
            self._Lrac_Arb__tab[d]=compte.Proportion()
            self._Lrac_Arb__tab[d].read_Compte(lc[d],**kw)

        v={}
        for a in nlc:
            v[a]=0
            for b in nlc:
                v[a]+=lc.inter(a,b)

        for a in nlc:
            for b in nlc:
                if v[a]!=0:
                    self._Lrac_Arb__pas[(a,b)]=float(lc.inter(a,b))/v[a]
                else:
                    self._Lrac_Arb__pas[(a,b)]=0

    def read_nf(self, nf):
        "Reads file of proportions with name $1"
        self.__init__()
        try:
            f = open(nf,'rU')
        except IOError, e:
            print "Unknown file: ", nf
            return
        s=f.readline()
        while s and s.find(':')==-1:
            s=f.readline()
        if not s:
            print "No descriptor in " + nf
            f.close()
            return

        tab=""
        while s and s.find(',')==-1:
            i=s.find(':')
            if i!=-1:
                try:
                    d=int(s[:i])
                except ValueError, e:
                    print "Bad descriptor in: " + s
                    self.__init__()
                    f.close()
                    return

                tab=self._Lrac_Arb__tab.setdefault(d,compte.Proportion())
            else:
                t=s.split()
                if t!=[]:
                    if len(t)<2:
                        print "Problem at line: " + s
                        self.__init__()
                        f.close()
                        return
                    d=t[0].split("|")
                    if len(d)!=2:
                        print "Problem at line: " + s
                        self.__init__()
                        f.close()
                        return
                    tab._Proportion__add(d[0],d[1],float(t[1]))
            s=f.readline()

        while s:
            t=s.split()
            if t!=[]:
                tt=t[0].split(',')
                if len(tt)==2:
                    try:
                        if float(t[1])>1.0:
                            print "Bad proportion at line: " + s
                            self.__init__()
                            f.close()
                            return
                        self._Lrac_Arb__pas[(int(tt[0]),int(tt[1]))]=float(t[1])
                    except ValueError, e:
                        print "Bad transition in: " + s
                        self.__init__()
                        f.close()
                        return
                else:
                    print "Problem at line " + s
                    self.__init__()
                    f.close()
                    return
            s=f.readline()

        for i in self._Lrac_Arb__tab:
            for j in self._Lrac_Arb__tab:
                self._Lrac_Arb__pas.setdefault((i,j),0)
                
        f.close()


    def loglex(self):
        """Write as a string for a Lexique, using logarithms of
proportions.
"""
        st=""
        for m in self.num():
            st+=str(m)+": "+self._Lrac_Arb__tab[m].loglex()+"\n" 
            
        for m in self.num():
            for n in self.num():
                st+= str(m)+","+str(n)+"\t"
                x=self._Lrac_Arb__pas[(m,n)]
                if x>0:
                    st+=str(math.log(x))
                else:
                    st+="-10000"
                st+="\n"
                
        return st

        
############################################################
#### Calculs
    
    def lg_max_prior(self):
        "Return the length of the longest prior."
        x=0
        for i in self._Lrac_Arb__tab.values():
            y=i.lg_max_prior()
            if y>x:
                x=y
        return x
    
    def lg_max_posterior(self):
        "Return the length of the longest posterior."
        x=0
        for i in self._Lrac_Arb__tab.values():
            y=i.lg_max_posterior()
            if y>x:
                x=y
        return x
    
    def KL_MC(self, lp2, nb=100, lg=1000):
        """Compute Kullback-Leibler divergence to Lproportion lp2 with
Monte Carlo simulation on nb=100 Sequence of length lg=1000.
"""
    
        if nb <= 0:
            print "Too few sequences"
            return

        if lg<=1:
            print "Too short sequences"
            return
        
        lx1=lexique.Lexique()
        lx1.read_Lprop(self)
        lx2=lexique.Lexique()
        lx2.read_Lprop(lp2)
        
        g=sequence.Sequence()
        p=partition.Partition()
        v=0.0
        for i in range(nb):
            print i,'\r',
            sys.stdout.flush()
            g.read_Lprop(self,long=lg)
            p.viterbi(g,lx1)
            v+=p.val()
            p.viterbi(g,lx2)
            v-=p.val()
        v/=nb
        return v/(lg-1)
