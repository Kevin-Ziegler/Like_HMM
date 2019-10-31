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
import string

import lcompte
import descripteur 
from Modules.Clexique import *

import matrice
import sequence

class Lexique:
    "Lexique"

    def __init__(self, **kw):
        """ Keyword argument:
str -- build from string str;
alpha -- alph (with keyword str), uses alphabet alpha;
Lprop -- build from Lproportion Lprop;
fic -- build from filename fic;
fprop -- build from Lproportion file of name fprop;
"""
        self.__lex=Clexique()
        if kw.has_key('str'):
            self.read_str(kw['str'],kw.get('alpha',""))
        elif kw.has_key('Lprop'):
                self.read_Lprop(kw['Lprop'])
        elif kw.has_key('fic'):
            self.read_nf(kw['fic'])
        elif kw.has_key('fprop'):
            lp=lcompte.Lproportion(fic=kw['fprop'])
            self.read_Lprop(lp)
            del lp

##################################
##  creation
        
    def read_nf(self,nf,ns=""):
        """Build from filename nf and alphabet ns=""."""
        self.__lex.read_fich(nf,ns)

    def read_str(self,nf,ns=""):
        """Build from string nf and alphabet ns=""."""
        self.__lex.read_str(nf,ns)

    def __setitem__(self, i, x):
        """If i is int : add the COPY of Descripteur x to number i;
If i is a tuple of int: build the descriptor pattern from the tuple or list of
Descripteur or string x .
"""
        lsn=self.ls_num()
        if type(i)==int:
            if i in lsn:
                self.__lex.__setitem__(i,x._Descripteur__desc)
                return
            else:
                s=str(i)
                st=str(x)
        elif type(i)==tuple:
            s=""
            st=""
            if len(i)!=len(x):
                print "Different lengths between tuple and list"
            for j in range(len(i)):
                if i[j] in lsn:
                    print "Bad descriptor number ", i[j], " already used"
                    return
                s+=str(i[j])+','
                st+=str(x[j])
            s=s[:-1]
        else:
            print "Bad descriptor type ", i
            return

        self.__lex.aj_str(s+":"+st)

    def __iadd__(self, lex):
        """Add the COPYs of the Descripteurs of Lexique lex. The already
existing Descripteur numbers of self are replaced by the ones of lex.
"""
        for d in lex:
            self.__lex.aj_str(str(d))
        return self
    
    def read_Lprop(self, lp):
        """Build from Lproportion lp. Compute automatically
log-probabilites, or -10000 if log not possible.
"""
        lpn=lp.num()
        for i in lpn:
            self[i]=lp[i].loglex(i)
        
        self.__lex.init_trans();
        for d in lpn:
            for f in lpn:
                x=lp.inter(d,f)
                if x>0:
                    x=math.log(x)
                else:
                    x=-10000
                if self.__lex.g_trans(d,f,x)==0:
                    print "Problem of transition between %d and %d"%(d,f)

    def g_inter(self, a, b, v):
        """Set the probability of transition between descriptors."""
        if (v<0) or (v>1):
            print "Bad probability value: ",v
            return

        if self.__lex.g_trans(a,b,math.log(v))==0:
            self.__lex.init_trans_vers(b)
            self.__lex.g_trans(a,b,math.log(v))
        
    def met_au_net(self):
        """Remove identical patterns and repetitions in patterns."""
        self.__lex.met_au_net()

    def __delitem__(self, i):
        "Remove the descriptor number i ( x.__delitem__(i) <==> del x[i] )."
        if i in self.ls_num():
            self.__lex.enleve(i)

###################################
#### calculs

    def prediction(self, D, **kw):
        """Return the prediction of the best descriptor on data D.

Keyword arguments:
deb -- first position of the computed segment of the data (default:0);
fin -- last position of the computed segment of the data
    (default: the last one).
"""
        
        d=kw.get("deb",0)
        f=kw.get("fin",-2)
        if isinstance(D, matrice._Matr):
            return self.__lex.pred(D._Matr__c_elem(),d,f)
        elif isinstance(D, sequence._Seq):
            return self.__lex.pred(D._Seq__c_elem(),d,f)

    def val_max(self, D, **kw):
        """Return the maximum prediction possible on data D.

Keyword arguments:
deb -- first position of the computed segment of the data (default:0);
fin -- last position of the computed segment of the data
    (default: the last one).
"""
        
        d=kw.get("deb",0)
        f=kw.get("fin",len(D))
        if isinstance(D, matrice._Matr):
            return self.__lex. val_max(D._Matr__c_elem(),d,f)
        elif isinstance(D, sequence._Seq):
            return self.__lex.val_max(D._Seq__c_elem(),d,f)

    def llh(self, D, **kw):
        """Return the best log-likelihood on sequence D.

Keyword arguments:
deb -- first position of the computed segment of the data (default:0);
fin -- last position of the computed segment of the data
    (default: the last one).
"""
        d=kw.get("deb",0)
        f=kw.get("fin",-2)
        if isinstance(D, sequence._Seq):
            return self.__lex.llh(D._Seq__c_elem(),d,f)
        
    def ls_evalue(self, D, **kw):
        """Return the dictionnary {tuple of descriptors
numbers:prediction of this (pattern of) descriptor on D}.

Keyword arguments:
deb -- first position of the computed segment of the data (default:0);
fin -- last position of the computed segment of the data
       (default: the last one).
"""
        d=kw.get("deb",0)
        f=kw.get("fin",-2)
        
        if isinstance(D, matrice._Matr):
            rep=self.__lex.ecrit_evalue(D._Matr__c_elem(),d,f)
        elif isinstance(D, sequence._Seq):
            rep=self.__lex.ecrit_evalue(D._Seq__c_elem(),d,f)
        if rep!="":
            return eval(rep)    
        return {}
        
    def windows(self, D, t, p):
        """On data D, return the list of best predictions on a sliding
window of size t with slidings steps of size p.
"""
        lv=[]
        lg=len(D)-t+1
        i=0
        while i<lg:
            lv.append(self.prediction(D,deb=i,fin=i+t-1))
            i+=p
        return lv

    def log_likelihood(self, D, n):
        """Return the list of the log-likelihoods of the data D
on the segmentations up to n classes.
"""
        if isinstance(D, matrice._Matr):
            return self.__lex.log_vraisemblance(D._Matr__c_elem(),n)
        elif isinstance(D, sequence._Seq):
            return self.__lex.log_vraisemblance(D._Seq__c_elem(),n)
        else:
            return []
        
    def __c_elem(self):
        return self.__lex

############################################
###   sorties
            
    def __str__(self):
        """(x.__str__()<==> str(x))"""
        return str(self.__lex)
        
    def __len__(self):
        "Return the number of descriptors."
        return self.__lex.nb_desc()

    def ls_num(self):
        "Return the list of descriptors numbers."
        return eval(self.__lex.ls_num())

    def is_empty(self):
        return self.__lex.est_vide()==1

    def __iter__(self):
        "Iterator on descriptors. Use:  for element in l."
        return Lexique_iter(self)
            
    def __getitem__(self, i):
        """Return a COPY of descriptor number i.
        (x.__getitem__(i) <==> x[i]).
"""
        a=self.__lex.__getitem__(i)
        d=descripteur.Descripteur(i)
        d._Descripteur__desc=a
        return d

#################################################
############################

class Lexique_iter:

    def __init__(self,lx):
        self.__lex=lx
        self.__lnum=self.__lex.ls_num()
        self.__ln=len(self.__lnum)
        self.__ind=-1

    def next(self):
        if self.__ind==self.__ln-1:
            raise StopIteration
        else:
            self.__ind+=1
            return self.__lex[self.__lnum[self.__ind]]
        
            
