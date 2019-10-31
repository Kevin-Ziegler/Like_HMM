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

import string
import math
import random

import descripteur
import sequence
import lexique

########################################################################
########################################################################
############# classe _Arbre dont heritent Compte et Proportions

class _Arbre:
    "Tree of words, structured as a catalog of _Arbre"

    def __init__(self, **kw):
        """Keyword argument:
fic -- Build from filename f.
"""
        self.__cat={}
        self.__nbe=0
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])


    def read_nf(self, nf):
        "Build from filename nf."
        self.__init__()
        try:
            f = open(nf,'rU')
        except IOError, e:
            print "Unknown file: ", nf
            return
        s=f.readline()
        while s:
            t=s.split()
            if t!=[]:
                if len(t)<2:
                    print "Problem at line: " + s
                    self.__init__()
                    f.close()
                    return
                self.__add(t[0],float(t[1]))
            s=f.readline()
        f.close()


    def __somme(self):
        "Return the sum of all nodes."
        b=self.__nbe
        for f in self.__cat.values():
            b+=f.__somme()
        return b

    def __idiv__(self, v):
        """Divide each node by value v (x.__idiv(v) <==> x/= v)."""
        if v!=0:
            self.__nbe/=v
            for f in self.__cat.values():
                f/=v

###########################################
####  sorties

    def lg_max(self):
        "Return the length of the longest word."
        if self.__cat=={}:
            return 0
        m=0
        for c in self.__cat.values():
            n=c.lg_max()
            if m<n:
                m=n
        return m+1


    def alph(self,t=[]):
        "Return the list of the letters."
        s=t[:]
        for c in self.__cat:
            if c!="^" and c not in s:
                s.append(c)
            s=self.__cat[c].alph(s)
        return s

    def __add(self,a,b):
        if isinstance(self,Compte):
            self._Compte__add(a,b)
        elif isinstance(self,Proportion):
            self._Proportion__add(a,b)

    def is_empty(self):
        "Return True if dictionary is empty."
        return self.__cat=={}
    
##################################################################
##################################################################
##################################################################
#####  classe Compte
    
class Compte(_Arbre):
    
    def add_seq(self, s, lg, **kw):
        """Add the counts of words at most lg-length from sequence s.
Needs operator s[].
Character '^' is for beginnings and ends of sequences.
         
Keyword argument:
deb -- Count only after position deb (>=0) included;
fin -- Count only before position fin (<len()) included;
alpha -- Count only words which letters are in string alpha. If
         alpha='', do not consider alpha;
fact -- Count each word fact (default: 1).
"""

        if lg<=0:
            return
        
        f=kw.get('fact',1)

        fin=kw.get('fin',len(s)-1)
        deb=kw.get('deb',0)
        if deb<0 or deb>fin:
            return

        alpha=kw.get('alpha','')
        
        if alpha=='':
            self.__add_ds_seq(s,deb,fin,lg,f)
        else:
            dalpha={}
            for x in alpha:
                dalpha[x]=1
            self.__add_ds_seq_sur_alph(s,deb,fin,lg,dalpha,f)


    def add_pseudo(self, x, val=1):
        """Add the counts of the word x with optionnal value val=1.
Only the count of the given word are added, and not its prefixes.
"""
        self.__add(x,val)
        self.__add(x[:-1],-val)
            
    def __iadd__(self, c):
        "Add counts of Compte c (x.__iadd__(c) <==> x+=c)."
        self._Arbre__nbe+=c._Arbre__nbe
        for i,f in c._Arbre__cat.items():
                self._Arbre__cat.setdefault(i,Compte()).__iadd__(f)
        return self
    
##########################################
#### donnees/calculs

    def __getitem__(self,s):
        """Return count of word s. '.' is the wildcard, "^" excepted.
(x.__getitem__(s) <==> x[s]).
"""
        if len(s)==0:
            return self._Arbre__nbe
        if s[0]=='.':
            a=0
            for i in self._Arbre__cat:
                if i!="^":
                    a+=self._Arbre__cat[i][s[1:]]
            return a
        if self._Arbre__cat.has_key(s[0]):
            return self._Arbre__cat[s[0]][s[1:]]
        else:
            return 0


    def prop(self, **kw):
        """Return the corresponding Proportion:
        
Keyword argument:
lpost -- length of the posterior words (ie on the right) (default: max);
lprior -- length of the prior words (ie on the left) (default: 0).
"""

        p=Proportion()
        p.read_Compte(self, **kw)
        return p
    

    def restrict_to(self, alph):
        """Return the Compte restricted to letters of string alph.
Keep the ends ^.
"""
        nc=Compte()
        nc._Arbre__nbe=self._Arbre__nbe
        for i,f in self._Arbre__cat.items():
            nc._Arbre__nbe-=f._Arbre__nbe
            if i=="^" or i in alph:
                c=f.restrict_to(alph)
                nc._Arbre__cat[i]=c
                nc._Arbre__nbe+=c._Arbre__nbe
        return nc

    def strip(self,d=1):
        """Return the Compte without characters ^."""
        nc=Compte()
        nc._Arbre__nbe=self._Arbre__nbe
        for i,f in self._Arbre__cat.items():
            if i!="^":
                nc._Arbre__cat[i]=f.strip(0)
            elif d:
                nc._Arbre__nbe-=f._Arbre__nbe
        return nc

    def rstrip(self,d=1):
        """Return the Compte without ending characters ^."""
        nc=Compte()
        a=0
        for i,f in self._Arbre__cat.items():
            if i!="^":
                nc._Arbre__cat[i]=f.rstrip(0)
                a+=f._Arbre__nbe
            elif d:
                c=f.rstrip(True)
                if c:
                    nc._Arbre__cat["^"]=c
                    a+=c._Arbre__nbe
        if not d:
            nc._Arbre__nbe=self._Arbre__nbe
        else:
            nc._Arbre__nbe=a

        if nc._Arbre__nbe==0:
            return
        else:
            return nc

    def min(self, a):
        """Return the Compte of the minimum between a and self.
"""
        c=Compte()

        for i,f in self._Arbre__cat.items():
            if a._Arbre__cat.has_key(i):
                c._Arbre__cat[i]=f.__min(a._Arbre__cat[i])

        for f in c._Arbre__cat.values():
            c._Arbre__nbe+=f._Arbre__nbe
        return c

    def max(self, a):
        """Return the Compte of the maximum between a and self.
"""
        c=Compte()

        c._Arbre__nbe=max(self._Arbre__nbe,a._Arbre__nbe)
        
        lk=self._Arbre__cat.keys()
        for k in a._Arbre__cat:
            if not self._Arbre__cat.has_key(k):
                lk.append(k)
        
        for i in lk:
            if self._Arbre__cat.has_key(i):
                if a._Arbre__cat.has_key(i):
                    c._Arbre__cat[i]=self._Arbre__cat[i].max(a._Arbre__cat[i])
                else:
                    c._Arbre__cat[i]=self._Arbre__cat[i].copy()
            else:
                c._Arbre__cat[i]=a._Arbre__cat[i].copy()

        return c

    def intersects(self, a):
        """Return the Compte of the counts of self restricted to the
words of a.
"""

        c=Compte()

        for i in a._Arbre__cat:
            if self._Arbre__cat.has_key(i):
                b=self._Arbre__cat[i].__intersects(a._Arbre__cat[i])
                if b._Arbre__nbe!=0:
                    c._Arbre__cat[i]=b

        for f in c._Arbre__cat.values():
            c._Arbre__nbe+=f._Arbre__nbe
        return c


    def copy(self):
        "Return a copy of this Compte"
        c=Compte()
        c._Arbre__nbe=self._Arbre__nbe
        for i,f in self._Arbre__cat.items():
            c._Arbre__cat[i]=f.copy()
            
        return c
        
###########################################
####  sorties

    def pref(self, l):
        "Return the string of counts of l-length words."
        if l<0:
            return ""
        else:
            return self.__pref(l,"")
        
    def next(self, s):
        "Return the list of [letter, value] which s in the prefix."
        if len(s)==0:
            l=[]
            for i,j in self._Arbre__cat.items():
                l.append([i,j._Arbre__nbe])
            return l
        else:
            if self._Arbre__cat.has_key(s[0]):
                return self._Arbre__cat[s[0]].next(s[1:])
            else:
                return []            

    def has_prefix(self, s):
        """Return True iff s is a STRICT prefix (^ excluded), else False."""
        if len(s)==0:
            l=len(self._Arbre__cat)
            return not (l==0  or (l==1 and self._Arbre__cat.has_key(["^"])))
        else:
            if self._Arbre__cat.has_key(s[0]):
                return self._Arbre__cat[s[0]].has_prefix(s[1:])
            else:
                return False

    def __str__(self):
        """(x.__str__()<==> str(x))"""
        return self.__ecrit("")


    def words(self,s=""):
        "Return the list of the words."
        if self._Arbre__cat=={}:
            return [s]

        if self._Arbre__nbe!=0 and s!="":
            l2=[s]
        else:
            l2=[]

        for c,f in self._Arbre__cat.items():
            l2+=f.words(s+c)
        return l2


################################################
### prive

    def __ecrit(self,st):
        if self._Arbre__cat=={}:
            return st+"\t"+str(self._Arbre__nbe)+"\n"

        st2=""
        a=self._Arbre__nbe
        for i,c in self._Arbre__cat.items():
            st3=c.__ecrit(st+i)
            st2+=st3
            a-=c._Arbre__nbe

        if a>0:
            st2+=st+"\t"+str(a)+"\n"

        return st2


    def __add_ds_seq(self, s, deb, fin, lg, f):
        """ private """
        if fin>=len(s) or deb<0:
            return

        self.__add_suff(s,deb,deb+lg-2,f)
        
        i=deb
        while i<=fin-lg+1:
            self.__add_word(s,i,i+lg-1,f)
            i+=1

        while i<=fin:
            self.__add_pref(s,i,fin,lg,f)
            i+=1


    def __add_ds_seq_sur_alph(self, s, deb, fin, lg, dalph, f):
        """ private """
        if dalph=={}:
            self.__add_ds_seq(s,deb,fin,lg,f)
            return
        
        if fin>=len(s) or deb<0:
            return

        i=fin

        j=0
        while i>=deb:
            if not dalph.has_key(s[i]):
                if j!=0:
                    self.__add_suff(s,i+1,i+j,f)
                j=0
            else:
                self.__add_pref(s, i, i+j, lg, f)
                if j<lg-1:
                    j+=1
            i-=1

        while j>=1:
            self.__add_suff(s,i+1,i+j,f)
            j-=1

    def __add(self, st, val=1):
        """Recursively increment Compte, with word st and value val=1.
Needs st[] and len(st)."""
        self.__add_word(st,0,len(st),val)        

    def __add_word(self,s,i,j,f):
        """Add $1[$2:$3+1], with value $4."""
        self._Arbre__nbe+=f
        if i<len(s) and j>=i:
            self._Arbre__cat.setdefault(s[i],Compte()).__add_word(s,i+1,j,f)


    def __add_pref(self, s, i, j, lg, f):
        """Add $1[$2:$3+1]+'^'*($4-($3-$2)), with value $5."""
        self._Arbre__nbe+=f
        if j>=i and lg>=1:
            self._Arbre__cat.setdefault(s[i],Compte()).__add_pref(s,i+1,j,lg-1,f)
        elif lg>=1:
            self._Arbre__cat.setdefault("^",Compte()).__add("^"*(lg-1),f)
            
        
    def __add_suff(self, s, i, j, f):
        """Add '^'+$1[$2:$3+1], with value $4."""
        self._Arbre__nbe+=f
        self._Arbre__cat.setdefault("^",Compte()).__add_word(s,i,j,f)
        
    def __pref(self, l, st):
        if l==0:
            return st+"\t"+str(self._Arbre__nbe)+"\n"
        if self._Arbre__cat=={}:
            return ""
        
        st2=""
        for i,c in self._Arbre__cat.items():
            st3=c.__pref(l-1,st+i)
            st2+=st3

        return st2

    def __min(self, a):
        """Private part of min."""
        c=Compte()
        c._Arbre__nbe=min(self._Arbre__nbe,a._Arbre__nbe)

        for i,f in self._Arbre__cat.items():
            if a._Arbre__cat.has_key(i):
                c._Arbre__cat[i]=f.__min(a._Arbre__cat[i])

        return c

    def __intersects(self, a):
        """Private part of intersects."""

        c=Compte()
        c._Arbre__nbe=self._Arbre__nbe
        
        for i in a._Arbre__cat:
            if self._Arbre__cat.has_key(i):
                b=self._Arbre__cat[i].__intersects(a._Arbre__cat[i])
                if b._Arbre__nbe!=0:
                    c._Arbre__cat[i]=b

        return c


##################################################################
##################################################################
##################################################################
#####  classe Proportion


class Proportion(_Arbre):
            
    def __init__(self, **kw):
        """Keyword arguments:
fic -- Build from filename fic;
str -- Build from string str.
"""
        _Arbre.__init__(self)
        self.__post=Post()
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])
        elif kw.has_key('str'):
            self.read_str(kw['str'])
        
    def read_nf(self, nf):
        "Read file of name nf."
        self.__init__()
        try:
            f = open(nf,'rU')
        except IOError, e:
            print "Unknown file: ", nf
            return
        s=f.readline()
        while s:
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
                self.__add(d[0],d[1],float(t[1]))
            s=f.readline()
        f.close()

    def read_str(self, st):
        """Read string st, at same format as the file's."""
        self.__init__()
            
        lst=st.split("\n")
        for s in lst:
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
                self.__add(d[0],d[1],float(t[1]))

    def __iadd__(self, p):
        """Add to self the Proportion p."""

        lst=str(p).split('\n')
        for s in lst:
            t=s.split()
            if len(t)==2:
                lt=t[0].split("|")
                self.__add(lt[0],lt[1],float(t[1]))

        self.__somme_a_un()
        return self
        
    def __add(self, pr, po, val):
        """Add to the Proportion prior pr and posterior po, with value
val. Needs pr[:] and po[:]"""

        
        if len(pr)==0:
            self.__post._Post__add(po,val)
        elif pr[-1]=="^":
            self._Arbre__cat.setdefault("^",Proportion()).__post._Post__add(po,val)
        else:
            self._Arbre__cat.setdefault(pr[-1],Proportion()).__add(pr[:-1],po,val)


    def read_Compte(self, com, **kw):
        """Build from Compte com:
        
Keyword argument:
lpost -- length of the posterior words (ie on the right) (default: max);
lprior -- length of the prior words (ie on the left) (default: 0).

"""

        lprior=kw.get('lprior',0)
        if lprior<0:
            print "Bad prior", lprior
            return

        lpost=kw.get('lpost',-1) 

        self.__init__()
        lst=str(com).split('\n')
        for st in lst:
            t=st.split()
            if len(t)==2:
                if lpost>0:
                    b1=0
                    while b1>=0:
                        if not (lprior+lpost-b1>len(t[0]) or
                                (t[0].startswith("^",lprior-b1) and
                                 (t[0].endswith("^",0,lprior-b1) or lprior==b1))):
                            tps=t[0][lprior-b1:lprior+lpost-b1]
                            if lpost+lprior-b1>len(t[0]):
                                if t[0].endswith("^",):
                                    self.__add(t[0][:lprior-b1],
                                                  tps+"^"*(lpost-len(tps)), float(t[1]))
                            else:
                                self.__add(t[0][:lprior-b1],tps, float(t[1]))
                                
                        if t[0].startswith("^",0) and b1<lprior-1:
                            b1+=1
                        else:
                            b1=-1
                else:
                    b1=0
                    while b1>=0:
                        if not (t[0].startswith("^",lprior-b1) and
                                (t[0].endswith("^",0,lprior-b1) or lprior==b1)):
                            tps=t[0][lprior-b1:]
                            if len(tps)>0:
                                self.__add(t[0][:lprior-b1],tps, float(t[1]))

                        if t[0].startswith("^",0) and b1<lprior-1:
                            b1+=1
                        else:
                            b1=-1
            
            elif len(t)!=0:
                    print "Problem at ", st

        self.__somme_a_un()


    def limit_on(self, l):
        """ Return a SHALLOW copy of self restricted to the priors
that include the words of list or Compte l.
"""
        if isinstance(l,list):
            c=Compte()
            for w in l:
                d=c
                i=len(w)
                while i>0:
                    i-=1
                    d=d._Arbre__cat.setdefault(w[i],Compte())
                d._Arbre__nbe=1
            d=c
        else:
            d=c.reverse()

        return self.__limit_on(d,d)

    def __limit_on(self,cc,c):
        
        r=Proportion()
        
        for k,v in self._Arbre__cat.items():
            
            if cc[k]>0 or c[k]>0:
                r._Arbre__cat[k]=v
            elif cc.has_prefix(k):
                r._Arbre__cat[k]=v.__limit_on(cc._Arbre__cat[k],c)
                
            if (not r._Arbre__cat.has_key(k) or (r._Arbre__cat[k].is_empty() and not r._Arbre__cat[k].has_post())):
                r._Arbre__cat[k]=v.__limit_on(c,c)

        return r
    
######################################################
###### Calculs

    def KL_MC(self, p2, nb=100, lg=1000):
        """Compute KL-distance with Monte Carlo at Proportion p2 on
nb=100 Sequence of length lg=1000."""
    
        if nb <= 0:
            print "Too few sequences"
            return

        if lg<=1:
            print "Too short sequences"
            return

        lx=lexique.Lexique()
        lx[1]=self.loglex(1)
        lx[2]=p2.loglex(2)
        
        g=sequence.Sequence()
        
        v=0.0
        for i in range(nb):
            g.read_prop(self, long=lg)
            lv=lx.ls_evalue(g)
            v+=lv[1]-lv[2]

        v/=nb
        return v/(lg-1)


    def __getitem__(self,s):
        """Return the string of posterior of prior s (x.__getitem__(s)
<==> x[s])."""
        if len(s)==0:
            return str(self.__post)
        if self._Arbre__cat.has_key(s[-1]):
            return self._Arbre__cat[s[-1]][s[:-1]]
        else:
            return ""

    def alph(self,s=[]):
        t=self.__post.alph(s)
        return _Arbre.alph(self,t)

    def lg_max(self):
        "Return the length of the longest word (prior+posterior)."
        return max(self.__post.lg_max(),_Arbre.lg_max(self))

    def lg_max_prior(self):
        "Return the length of the longest prior."
        if self._Arbre__cat=={}:
            return 0
        m=0
        for c in self._Arbre__cat.values():
            n=c.lg_max_prior()
            if m<n:
                m=n
        return m+1

    def lg_max_posterior(self):
        "Return the length of the longest posterior."
        m=self.__post.lg_max()
        for d in self._Arbre__cat.values():
            n=d.lg_max_posterior()
            if n>m:
                m=n
        return m

    def has_post(self):
        "Return True if self has a non-empty posterior."

        return self.__post._Arbre__cat!={}
    
###########################################
####  sorties

    
    def __str__(self):
        """(x.__str__() <==> str(x))"""
        return self.__ecrit("")

    def __ecrit(self,st):
        st2=""
        if self.__post._Arbre__cat!={}:
            st2+=self.__post.ecrit(st+"|")
        for i,f in self._Arbre__cat.items():
            st3=f.__ecrit(i+st)
            st2+=st3
        return st2

    
    def loglex(self, n=0):
        "Build a new Descripteur of number n."
        s=self.__str_loglex()
        return descripteur.Descripteur(n,str=s)
    
    def prefixes(self,s=""):
        "Return the list of the prefixes."
        if self._Arbre__cat=={}:
            return [s]

        if self.__post.is_empty():
            l2=[]
        else:
            l2=[s]

        for c,f in self._Arbre__cat.items():
            l2+=f.prefixes(c+s)
        return l2


    def next(self, s):
        "Return the list of [word, value] which s in the prefix."
        if len(s)==0:
            return self.__post.next()
        elif self._Arbre__cat.has_key(s[-1]):
            return self._Arbre__cat[s[-1]].next(s[:-1])
        elif s[-1]==".":
            d=[]
            for k in self._Arbre__cat:
                d+=self._Arbre__cat[k].next(s[:-1])
            return d
        else:
            return []            

    def rand_next(self, s):
        """Return a string randomly chosen among the ones which s in
the prefix, following the proportions of this.
"""
        suiv=self.next(s)
        if suiv==[]:
            return ""

        y=0
        for t in suiv:
            y+=t[1]

        x=random.random()*y
        lsuiv=len(suiv)
            
        while x>=0 and lsuiv>0:
            lsuiv-=1
            x-=suiv[lsuiv][1]

        return suiv[lsuiv][0]

        
    def has_prefix(self, s):
        "Return True iff s is a STRICT prefix, else False."
        if len(s)==0:
            return self.__post._Arbre__cat!={} or self._Arbre__cat!={}
        
        elif self._Arbre__cat.has_key(s[-1]):
            return self._Arbre__cat[s[-1]].has_prefix(s[:-1])
        else:
            return 0

    
#########################################################
#####   prive

    def __somme_a_un(self):
        self.__post.somme_a_un()
        for f in self._Arbre__cat.values():
            f.__somme_a_un()

    def __str_loglex(self):
        if self._Arbre__cat!={}:
            s="|{"
            for i in self._Arbre__cat:
                s+=i+self._Arbre__cat[i].__str_loglex()
                if self.__post._Arbre__cat!={}:
                    s+="!`"+self.__post.loglex(1)+"'"
            s+="!!(-100000)}"
        else:
            s="`"+self.__post.loglex(1)+"'"
        return s


##################################################################
##################################################################
##################################################################
#####  classe Post

class Post(_Arbre):

    def __add(self, po, val):
        """Increase recursively the Post from word po and a value val.
Needs po[:]."""
        if len(po)==0:
            self._Arbre__nbe+=val
        elif po[0]=="^":
            if len(po)==1:
                self._Arbre__cat.setdefault("^",Post())._Arbre__nbe+=val
            else:
                self.__add(po[1:],val)
        else:
            self._Arbre__cat.setdefault(po[0],Post()).__add(po[1:],val)


    def somme_a_un(self):
        c=self._Arbre__somme()
        if c!=0:
            self/=c

#############################################################
##### sorties

    def loglex(self,i=0):

        s=""
        
        if self._Arbre__cat!={}:
            if i==1:
                s+="|("
            else:
                s+="|`"
                
            for j,c in self._Arbre__cat.items():
                s+=j+c.loglex(0)

            s+="!"
            
                
        if self._Arbre__nbe>0:
            s+="!("+`math.log(self._Arbre__nbe)`+")"
        else:
            s+="!(-100000)"

        if self._Arbre__cat!={}:
            if i==1:
                s+=")"
            else:
                s+="'"
                
        return s

    def __str__(self):
        return self.ecrit("")
    
    def ecrit(self,st):
        if self._Arbre__nbe!=0:
            st2= st+"\t"+`self._Arbre__nbe`+"\n"
        else:
            st2=""
            
        for i,c in self._Arbre__cat.items():
            st3=c.ecrit(st+i)
            st2+=st3
            
        return st2

#     def __getitem__(self, s):
#         """Returns the proportion of s.
#         (x.__getitem__(s) <==> x[s])"""
#         if s=="":
#             return self._Arbre__nbe
#         else:
#             if self._Arbre__cat.has_key(s[0]):
#                 return self._Arbre__cat[s[0]][s[1:]]
#             else:
#                 return self._Arbre__nbe

    def next(self,s=""):
        if self._Arbre__nbe!=0:
            l=[[s,self._Arbre__nbe]]
        else:
            l=[]

        for i,f in self._Arbre__cat.items():
            l+=f.next(s+i)

        return l
    

