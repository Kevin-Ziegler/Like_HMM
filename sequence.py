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

import random 
import string
import math

from Modules.Csequence import *
from Modules.Fsequence import *

import partition
from segment import Segment

class _Seq:
    "virtual Sequence"

    def __init__(self):
        self.__gen=Fsequence()
        self.__nom=""
        
    def __c_elem(self):
        "Return C++ object"
        return self.__gen
    

#########################################
### modifications

    def g_name(self, s):
        "Take name s"
        self.__nom=s

    def __setitem__(self, i, c):
        "(x.__setitem__(i,c) <==> x[i]=c)"
        self.__gen[i]=c

    def __setslice__(self, i, j, s):
        """(x.__setslice__(i,j,s) <==> x[i:j]=s)
Replace the subsequence x[i:j] by Sequence or string s.
If len(s) <> j-i, builds a new Sequence as a result,
otherwise replace in the former one.
"""
        if i<0:
            i=0
        if j>len(self):
            j=len(self)
        ls=len(s)
        if ls==j-i:
            for k in range(i,j):
                self[k]=s[k-i]
        else:
            g2=Csequence()
            lg2=len(self)-(j-i)+ls
            g2.genere(lg2)            
            k=0
            while k<i:
                g2[k]=self[k]
                k+=1
            while k<i+ls:
                g2[k]=s[k-i]
                k+=1
            while k<lg2:
                g2[k]=self[k-ls+(j-i)]
                k+=1
            self.__gen=g2
            
    def shuffle(self,i=0):
        """Quasi-uniformly randomize itself using i (default:
len*(log(len)+1)/2) transpositions.
"""
        if i==0:
            i=(int)(len(self)*(math.log(len(self))+1)/2)

        self.__gen.melange(i)

    def read_Lprop(self, lprop, **kw):
        """Build from a Lproportion lprop. Return the Partition of the
descriptors.
        
Keyword argument:
deb -- change only after position deb (>=0) included;
fin -- change only before position fin (<len()) included;
long -- create a lg-length Sequence. In that case, deb and
        fin are not read;
etat_init --  begin with descriptor number etat_init if it is valid.
              Otherwise, starts with a random descriptor of lprop.
"""

        al=lprop.alph()
        if al==[] or al==["^"]:
            print "Empty Lproportion"
            self.__init__()
            return

        p=partition.Partition()

        e=kw.get('etat_init',-1)
    
        if kw.has_key('long'):
            if not isinstance(self, Sequence):
                print "impossible generation of virtual sequence"
                return p
            fin=kw['long']
            if fin<=0:
                return p
            self.generate(fin)
            fin-=1
            deb=0
        else:
            self.__gen.termine(self.__gen.vtaille()-1)
            fin=kw.get('fin',len(self)-1)
            fin=min(fin,len(self))
            deb=kw.get('deb',0)
            if deb<0 or deb>fin:
                return p

        lik=lprop.num()
        if lik==[]:
            return p

        if deb!=0:
            p+=Segment(deb=0,fin=deb-1)
            
        def sum(x,y):
            return x+y

        # dicos des transitions entre etats
        ltrans={}
        llik=len(lik)
        for b in lik:
            sb=reduce(sum, [lprop.inter(b,x) for x in lik])
            ltrans[b]={}
            if sb==0:
                for x in lik:
                    ltrans[b][x]=1.0/llik
            else:
                for x in lik:
                    ltrans[b][x]=float(lprop.inter(b,x))/sb
                    
        ## Demarrage avec choix uniforme de l'etat initial ou bien e        

        if e in lik:
            etat=e
        else:
            etat=random.choice(lik)

        tab=lprop[etat]
        
        dseg=deb
        ilal=1.0/len(al)
        asuiv=[[x,ilal] for x in al]
        

        
        for i in range(deb,fin):

            ##choix de la lettre

            j=i-1
            s=""
            while j>=0:
                s=self.__gen[j]+s
                if not tab.has_prefix(s):
                    s=s[1:]
                    break
                else:
                    j-=1

            suiv=tab.next(s)
            if suiv==[]:
                suiv=asuiv

            y=reduce(sum ,[t[1] for t in suiv])
            x=random.random()*y

            lsuiv=len(suiv)            
            while x>=0 and lsuiv>0:
                lsuiv-=1
                x-=suiv[lsuiv][1]

            if len(suiv[lsuiv][0])!=1:
                print "Bad proportion after " + sq[1:]
                self.__init__()
                return
            
            a=suiv[lsuiv][0][0]
            if a=="^":
                for j in range(i,fin+1):
                    self.__gen[j]="\0"
                self.__gen.termine(i-1)
                if dseg<i:
                    p+=Segment(deb=dseg,fin=i-1,num=[etat])
                return p
            else: 
                self.__gen[i]=a

            ##choix de l'etat suivant

            llik=len(lik)
            x=random.random()
            while x>=0 and llik>0:
                llik-=1
                x-=ltrans[etat][lik[llik]]

            if etat!=lik[llik]:
                p+=Segment(deb=dseg,fin=i,num=[etat])
                dseg=i+1
                etat=lik[llik]
                tab=lprop[etat]


        ##choix de la lettre finale

        j=fin-1
        s=''
        while j>=0:
            s=self.__gen[j]+s
            if not tab.has_prefix(s):
                s=s[1:]
                break
            else:
                j-=1
                
        suiv=tab.next(s)
        if suiv==[]:
            suiv=asuiv

        y=reduce(lambda x,y: x+y ,[t[1] for t in suiv])
        x=random.random()*y
        
        lsuiv=len(suiv)            
        while x>=0 and lsuiv>0:
            lsuiv-=1
            x-=suiv[lsuiv][1]

        a=suiv[lsuiv][0][0]
        if a=="^":
            self.__gen.termine(fin-1)
            self.__gen[fin]="\0"
            if dseg<fin:
                p+=Segment(deb=dseg,fin=fin-1,num=[etat])
            return p
        else: 
            self.__gen[fin]=a
            p+=Segment(deb=dseg,fin=fin,num=[etat])

        if fin<len(self)-1:
            p+=Segment(deb=fin+1,fin=len(self)-1)
            
        return p


    def read_prop(self, prop, **kw):
        """Build from a Proportion prop. 

Keyword argument:
deb -- change only after position deb (>=0) included;
fin -- change only before position fin (<len()) included;
long -- create a lg-length Sequence. In that case, deb and
        fin are not read.
"""


        al=prop.alph()
        if al==[] or al==['^']:
            print "Empty Proportion"
            self.__init__()
            return

        asuiv=[[x,1.0/len(al)] for x in al]
        
        if kw.has_key('long'):
            if not isinstance(self, Sequence):
                print "impossible generation of virtual sequence"
                return p
            fin=kw['long']
            if fin<=0:
                return
            self.generate(fin)
            fin-=1
            deb=0
        else:
            self.__gen.termine(self.__gen.vtaille()-1)
            fin=kw.get('fin',len(self)-1)
            fin=min(fin,len(self)-1)
            deb=kw.get('deb',0)
            if deb<0 or deb>fin:
                return
            
        def sum(x,y):
            return x+y

        for i in range(deb,fin+1):
            j=i-1
            s=""
            while j>=0:
                s=self.__gen[j]+s
                if not prop.has_prefix(s):
                    s=s[1:]
                    break
                else:
                    j-=1

            suiv=prop.next(s)
            if j==-1:
                suiv+=prop.next("^"+s)

            if suiv==[]:
                suiv=asuiv

            y=reduce(sum ,[t[1] for t in suiv])
            x=random.random()*y
            lsuiv=len(suiv)
            
            while x>=0 and lsuiv>0:
                lsuiv-=1
                x-=suiv[lsuiv][1]

            a=suiv[lsuiv][0][0]
            if a=="^":
                self.__gen.termine(i-1)
                for j in range(i,fin+1):
                    self.__gen[i]="\0"
                break
            else: 
                self.__gen[i]=a

###########################################
### donnees

    def name(self):
        "Return the name."
        return self.__nom
            
    def __getitem__(self, i):
        "(x.__getitem__(i) <==> x[i])"
        return self.__gen[i]

    def __len__(self):
        "(x.__len__() <==> len(x))"
        return len(self.__gen)

    def alpha(self):
        "Return the list of the used letters."
        st=[]
        for i in self:
            if not i in st:
                st.append(i)
        return st

    def __getslice__(self,i,j):
        """!!! Do NOT create a new Sequence; so destruction of the original
Sequence entails destruction of this result.
(x.__getslice__(i,j) <==> x[i:j])"""
        nv=_Seq()
        nv.__c_elem().recup_rel(self.__c_elem(),i,j-1)
        nv.g_name(self.name())
        return nv

    def copy(self):
        "Return a NEW copy Sequence of the Sequence."
        g=Sequence()
        g.__gen.copie(self.__c_elem())
        g._Seq__nom=self._Seq__nom
        return g

############################################
###   sorties

    def __str__(self):
        """(x.__str__()<==> str(x))"""
        return str(self.__gen)
    
    def fasta(self, lg=80):
        "Return the string in fasta format."
        s=">" + str(self.__nom) + '\n'
        j=0
        if lg==0:
            lg=len(self)
        if len(self)>0:
            for i in self:
                s+=i
                j+=1
                if j==lg:
                    s+="\n"
                    j=0
            s+="\n"
        return s
	
    def seq(self):
        "Return the mere sequence."
        s=""
        j=0
        if len(self)>0:
            for i in self:
                s+=i
        return s

    


#######################################################################
#######################################################################
########  Classe Sequence

class Sequence(_Seq):
    "Sequence"

    def __init__(self, **kw):
        """Keyword argument:
fic -- build from filename fic.
"""
        _Seq.__init__(self)
        self._Seq__gen=Csequence()
        if kw.has_key('fic'):
            self.read_nf(kw['fic'])

    def generate(self,l):
        "Build empty with length l."
        self._Seq__gen.genere(l)

    def read_nf(self,nf):
        "Build from filename nf."
        self._Seq__gen.read_nf(nf)
        if nf[-3:]==".fa" or nf[-4:]==".fst" or nf[-6:]==".fasta":
            try:
                f=open(nf,'rU')
            except IOError, e:
                return
            
            l=f.readline()
            while l:
                if l[0]=='>':
                    self._Seq__nom=l[1:]
                    break
                l=f.readline()
            f.close()

#########################################
### modifications
    
    def read_Part(self, part, lprop):
        """Compute randomly from a Partition part and a Lproportion
lprop. Segments of part must be numbered, which numbers are those of
descriptors of lprop.
"""

        al=lprop.alph()
        if al==[] or al==['^']:
            print "Empty Lproportion"
            self.__init__()
            return

        asuiv=[[x,1.0/len(al)] for x in al]
        
        lg=part.len_don()
        if lg<=0:
            return
        ln=part.num()
        ln2=lprop.num()
        for i in ln:
            if not i in ln2:
                print "Bad Lproportion: ",i," not in the Lproportion"
                return

        self.generate(lg)

        for s in part:
            letat=[lprop[i] for i in s.num()]
            lle=len(letat)
            i=0
            for pos in range(s.deb(),s.fin()+1):
                tab=letat[i]

                ##choix de la lettre

                j=pos-1
                sq=""
                suiv=[]
                while j>=0:
                    sq=self._Seq__gen[j]+sq
                    if not tab.has_prefix(sq):
                        sq=sq[1:]
                        break
                    else:
                        j-=1

                suiv=tab.next(sq)                        
                if j==-1:
                    suiv+=tab.next("^"+sq)

                if suiv==[]:
                    suiv=asuiv

                x=random.random()
                lsuiv=len(suiv)
                while x>=0 and lsuiv>0:
                    lsuiv-=1
                    x-=suiv[lsuiv][1]

                if len(suiv[lsuiv][0])!=1:
                    print "Bad proportion after " + sq[1:]
                    self.__init__()
                    return

                if suiv[lsuiv][0]=='^':
                    for j in range(pos,lg):
                        self._Seq__gen[j]="\0"
                    self._Seq__gen.termine(pos-1)
                    return
                
                self._Seq__gen[pos]=suiv[lsuiv][0]
                
                i+=1
                if i>=lle:
                    i=0
