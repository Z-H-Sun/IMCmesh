#!/usr/bin/env ruby
# encoding: UTF-8
=begin
Created on Nov 22 2021

Output a string for Mathematica to calculate the Fourier series of a certain hkl index.

@author: ZSun
=end

puts "h = 1\nk = 1\nl = 3" # change hkl here
gets

def out(lx, ly, lz, func='Cos')
  str = ''
  for i in 0...lx.size
    str += "#{func}[2 Pi (h (#{lx[i]}) + k (#{ly[i]}) + l (#{lz[i]}))] +"
  end
  print("FullSimplify["+str.chop+"]")
  # these strings should be pasted to and executed in Mathematica to obtain the math expressions.
  gets
end

# O70 Fddd; obtained from ITC
lx = ["x","-x","-x","x","1/4-x","1/4+x","1/4+x","1/4-x",
"x","-x","-x","x","1/4-x","1/4+x","1/4+x","1/4-x",
"x+1/2","-x+1/2","-x+1/2","x+1/2","1/4-x+1/2","1/4+x+1/2","1/4+x+1/2","1/4-x+1/2",
"x+1/2","-x+1/2","-x+1/2","x+1/2","1/4-x+1/2","1/4+x+1/2","1/4+x+1/2","1/4-x+1/2"]

ly=["y","-y","y","-y","1/4-y","1/4+y","1/4-y","1/4+y",
"y+1/2","-y+1/2","y+1/2","-y+1/2","1/4-y+1/2","1/4+y+1/2","1/4-y+1/2","1/4+y+1/2",
"y","-y","y","-y","1/4-y","1/4+y","1/4-y","1/4+y",
"y+1/2","-y+1/2","y+1/2","-y+1/2","1/4-y+1/2","1/4+y+1/2","1/4-y+1/2","1/4+y+1/2"]

lz=["z","z","-z","-z","1/4-z","1/4-z","1/4+z","1/4+z",
"z+1/2","z+1/2","-z+1/2","-z+1/2","1/4-z+1/2","1/4-z+1/2","1/4+z+1/2","1/4+z+1/2",
"z+1/2","z+1/2","-z+1/2","-z+1/2","1/4-z+1/2","1/4-z+1/2","1/4+z+1/2","1/4+z+1/2",
"z","z","-z","-z","1/4-z","1/4-z","1/4+z","1/4+z"]

out(lx, ly, lz)
out(lx, ly, lz, 'Sin')

=begin
(111): a=16 (Cos[2 Pi x] Cos[2 Pi y] Cos[2 Pi z] + Sin[2 Pi x] Sin[2 Pi y] Sin[2 Pi z])
    -16 I (Cos[2 Pi x] Cos[2 Pi y] Cos[2 Pi z] + Sin[2 Pi x] Sin[2 Pi y] Sin[2 Pi z])
(022): b=16 (Cos[4 Pi (y - z)] + Cos[4 Pi (y + z)])
(202): c=16 (Cos[4 Pi (z - x)] + Cos[4 Pi (z + x)])
(220): d=16 (Cos[4 Pi (x - y)] + Cos[4 Pi (x + y)])
(004): e=32 Cos[8 Pi z]
(113): f=16 (Cos[2 Pi x] Cos[2 Pi y] Cos[2 Pi 3 z] - Sin[2 Pi x] Sin[2 Pi y] Sin[2 Pi 3 z])
    +16 I (Cos[2 Pi x] Cos[2 Pi y] Cos[2 Pi 3 z] - Sin[2 Pi x] Sin[2 Pi y] Sin[2 Pi 3 z])
(222): g=-32 I Sin[4 Pi x] Sin[4 Pi y] Sin[4 Pi z]

x = u
y = v/2
z = w/(2 Sqrt[3])
=end

# M15 C2/c; obtained from ITC
lx = ["x","-x","-x","x",
"1/2+x","1/2-x","1/2-x","1/2+x"]

ly = ["y","y","-y","-y",
"1/2+y","1/2+y","1/2-y","1/2-y"]

lz = ["z","1/2-z","-z","1/2+z",
"z","1/2-z","-z","1/2+z"]

out(lx, ly, lz)
out(lx, ly, lz, 'Sin')

=begin
(110): a=8 Cos[2 Pi x] Cos[2 Pi y]
(002): b=8 Cos[4 Pi z]
(021): c=-8 Sin[4 Pi y] Sin[2 Pi z] 
(111): d=-8 Sin[2 Pi y] Sin[2 Pi (x+z)] 
(112): e=8 Cos[2 Pi y] Cos[2 Pi (x+2 z)] 
=end

# T131 P4_2/mmc
lx = ["x","-x","-y","y",
"-x","x","y","-y",
"-x","x","y","-y",
"x","-x","-y","y",]

ly = ["y","-y","x","-x",
"y","-y","x","-x",
"-y","y","-x","x",
"-y","y","-x","x"]

lz = ["z","z","1/2+z","1/2+z",
"-z","-z","1/2-z","1/2-z",
"-z","-z","1/2-z","1/2-z",
"z","z","1/2+z","1/2+z"]

out(lx, ly, lz)
out(lx, ly, lz, 'Sin')

=begin
(110): a=8(Cos[2 Pi (x-y)]+Cos[2 Pi (x+y)])
(100): b=8(Cos[2 Pi x]+Cos[2 Pi y])
(101): c=8 (Cos[2 Pi x]-Cos[2 Pi y]) Cos[2 Pi z]
(002): d=16Cos[4 Pi z]
(112): e=16 Cos[2 Pi x] Cos[2 Pi y] Cos[4 Pi z] 
=end
