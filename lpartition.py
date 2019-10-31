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

import partition 
import lsequence
import matrice
import sequence

class Lpartition(list):
    "List of [data,Partition]"

    def add_Lseq(self, ls):
        "Append at the end of the data-list the data of Lsequence $1."
        for g in ls:
            self.append([g,0])

    def add_don(self, d, i = 1):
        "Append at the end of the data-list i times data d."
        if isinstance(d, matrice._Matr) or isinstance(d, sequence._Seq):
            for j in range(i):
                self.append([d,0])

    def build_random(self, l):
        "Create random l-Partition on the data-list."
        for x in self:
            p=partition.Partition()
            p.build_random(len(x[0]),l)
            x[1]=p
        
#     def append(self,i):
#         "Append at the end [data i[0], Partition i[1]]."
#         if len(i)==2:
#             if (isinstance(i[0], matrice._Matr) or \
#                 isinstance(i[0], sequence._Seq)) and \
#                 isinstance(i[1], partition.Partition):
#                 self.append(i)

########################################################
####### calculs
            
    def viterbi(self,l):
        """Compute the Partitions with Lexique l, using Viterbi
algorithm, on the already stored data.
"""
        for x in self:
            x[1]=partition.Partition()
            x[1].viterbi(x[0],l)

    def fb(self,l):
        """Compute the Partitions with Lexique l, using
forward-backward algorithm, on the already stored data. On each
position, the first best descriptor is kept.
"""
        m=matrice.Matrice()
        for x in self:
            x[1]=partition.Partition()
            m.fb(x[0],l)
            x[1].read_Matrice(m)
            
    def mpp(self, l, i):
        """Compute maximally predictive i-Partition with Lexique l,
on the already stored data.
"""
        for x in self:
            p=partition.Partition()
            p.mpp(x[0],l,i)
            x[1]=p
        
#####################################################
###  donnees

    def Lseq(self):
        "Return the corresponding Lsequence."

        lg=lsequence.Lsequence()
        for g,p in self:
            lg.append(g)
        return lg

    def str_part(self, i=0):
        """Return the string of Partitions.
If i=0 equals 1, outputs everything, else does not output the
descriptors.
"""
        st=""
        if i==1:
            for g,p in self:
                st+=str(p)
                st+="\n"
        else:
            for g,p in self:
                st+=p.abr()
                st+="\n"
        return st
