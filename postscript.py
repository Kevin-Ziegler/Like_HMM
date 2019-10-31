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

from math import *

def MOVE_TO(x,y):
    return " %g chx %g chy m\n" %(x,y)

def LINE_TO(x,y):
    return " %g chx %g chy l\n" %(x,y)

def TEXT_CENTER(x, y, s):
    return "(%s) %g chx %g chy tc\n" %(s,x,y)

def TEXT_DROIT(x, y, s):
    return "(%s) %g chx %g chy td\n" %(s,x,y)

def CURVE_TO(x1, y1, x2, y2, x3, y3):
    return "%g chx %g chy %g chx %g chy %g chx %g chy c\n" %(x1, y1, x2, y2, x3, y3)

def STROKE():
    return "stroke\n"

def NEWPATH():
    return "newpath\n"

def SETDASH(l):
    s="["
    for x in l[:2]:
        s+=str(x) + " "
    s+="] 0 setdash\n"
    return s

def SETLINEWIDTH(x):
    return "%g setlinewidth\n" %x


class Cadre:
    def __init__(self,xmin, ymin, xmax, ymax):
        "Defines the box from ($1,$2) to ($3,$4)"
        self.__xmin=xmin
        self.__xmax=xmax
        self.__ymin=ymin
        self.__ymax=ymax

    def prep_ps(self, f):
        "Sets the box of postcript file f"
        f.write("""%!PS-Adobe-5.0
%%BoundingBox: 20 0 590 780
%%Orientation: Landscape
%%EndComments
/chx { trx add echx mul } def
/chy { try add echy mul } def
/m { moveto } def
/l { lineto } def
/c { curveto } def
/t { moveto show } def
/tc {m dup stringwidth pop 2 div 0 exch sub 0 rmoveto show } def
/td {m dup stringwidth pop 0 exch sub 0 rmoveto show } def
/r { m l l l closepath stroke m } def
/b { m l l l closepath gsave 1 setgray fill grestore stroke m } def
/echx 1 def
/echy 1 def
/trx 0 def
/try 0 def

0 setlinewidth
90 rotate
/trx trx 39.78 add def
/try try 59.544 add def
/echx echx 716.04 mul def
/trx trx 716.04 div def
/echy echy 476.352 mul def
/try try 476.352 div def
/trx trx 0 add def
/try try -1.3 add def
""")

        entx=self.__xmax-self.__xmin
        if entx==0:
            entx=1
        enty=self.__ymax-self.__ymin
        if enty==0:
            enty=1
        echx=ceil(pow(10,floor(log10(entx))-1))
        echy=pow(10,floor(log10(enty)))

        s="""/echx echx %g mul def
/trx trx %g div def
/echy echy %g mul def
/try try %g div def
""" %(1.0/entx, 1.0/entx, 1.0/enty, 1.0/enty)
        s+="""/trx trx %g add def
/try try %g add def
/Helvetica-Narrow findfont [ 10 0 0 9 0 0] makefont setfont
""" %(-self.__xmin, -self.__ymin)
        f.write(s)

    def abscisses(self, f):
        "Draws the x-axis in PREPARED file f"

        f.write(NEWPATH())

        entx=self.__xmax-self.__xmin
        enty=self.__ymax-self.__ymin
        if enty==0:
            enty=1
        echx=ceil(pow(10,floor(log10(entx))-1))
        echy=pow(10,floor(log10(enty)))

        if self.__ymin >= 0:
            z=self.__ymin
        else:
            if self.__ymax < 0:
                z=self.__ymax
            else:
                z=0
        f.write(MOVE_TO(self.__xmin, z))
        f.write(LINE_TO(self.__xmax, z))
        if self.__ymax<0:
            u=0.01
        else:
            u=-0.02
            
        f.write(TEXT_CENTER(self.__xmin, z+enty*u, self.__xmin))
        if self.__xmin<0<self.__xmax:
            f.write(TEXT_CENTER(0, z+enty*u, 0))
            

        i=self.__xmin-(self.__xmin % 10)
        while i<self.__xmax-10*echx:
            j=1
            for j in range(0,10):
                if i+j*echx>=self.__xmin:
                    f.write(MOVE_TO(i+j*echx, z-enty*0.003)) 
                    f.write(LINE_TO(i+j*echx, z+enty*0.003))
            f.write(MOVE_TO(i+10*echx, z-enty*0.006)) 
            f.write(LINE_TO(i+10*echx, z+enty*0.006))
            f.write(TEXT_CENTER(i+10*echx, z+enty*u, i+10*echx))
            i+=10*echx
        while i<self.__xmax+1:
            f.write(MOVE_TO(i, z-enty*0.003)) 
            f.write(LINE_TO(i, z+enty*0.003))
            i+=echx 
        f.write(TEXT_CENTER(self.__xmax, z+enty*u, self.__xmax))

        f.write(STROKE())

    def ordonnees(self, f):
        "Draws the y-axis in PREPARED file f"

        f.write(NEWPATH())

        entx=self.__xmax-self.__xmin
        enty=self.__ymax-self.__ymin
        if enty==0:
            enty=1
        echx=ceil(pow(10,floor(log10(entx))-1))
        echy=pow(10,floor(log10(enty)))

        f.write(MOVE_TO(self.__xmin, self.__ymin))
        f.write(LINE_TO(self.__xmin, self.__ymax))
        f.write(TEXT_DROIT(self.__xmin-entx*0.01, self.__ymin, self.__ymin))
        f.write(TEXT_CENTER(self.__xmin, self.__ymax+enty*0.01, self.__ymax))
        
        if self.__ymin<0<self.__ymax:
            f.write(TEXT_DROIT(self.__xmin-entx*0.01,0, 0))
        
        z=echy*ceil(self.__ymin/echy);
        t=z-echy/10;
        while t>self.__ymin:
            f.write(MOVE_TO(self.__xmin-entx*0.003, t)) 
            f.write(LINE_TO(self.__xmin+entx*0.003, t))
            t-=echy/10;
  
        while z<self.__ymax:
            f.write(MOVE_TO(self.__xmin-entx*0.006, z)) 
            f.write(LINE_TO(self.__xmin+entx*0.006, z))    
            f.write(TEXT_DROIT(self.__xmin-entx*0.01, z, z))
            t=z+echy/10
            z+=echy
            while (t<z)  & (t<self.__ymax):
                f.write(MOVE_TO(self.__xmin-entx*0.003, t)) 
                f.write(LINE_TO(self.__xmin+entx*0.003, t))
                t+=echy/10;

        f.write(STROKE())

    def titre(self, f, st):
        "Writes title st in PREPARED file f"

        f.write(NEWPATH())
        f.write(TEXT_CENTER((self.__xmax+self.__xmin)/2,self.__ymax*1.05,st))
        f.write(STROKE())
