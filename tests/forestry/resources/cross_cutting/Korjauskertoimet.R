#  ohjelma laskee korjauspolynomin  y = b(1)*x + b(2)*x^2 + b(3)*x^3
#  kertoimet siten, ett[ polynomi kulkee seuraavan neljän pisteen kautta:
#    x1 = p[1] = (h-1.3)/h  (rinnankorkeus)   y(x1) = 0
#    x2 = p[2] = (h-6)/h    (6 m)             y(x2) = p[3] = dif
#    x3 = p[4]              (tukipiste)       y(x3) = p[5]
#    x4 = 0                 (latva)           y(x4) = 0
#
# Alkuperäinen ohjelma Snellman cpoly3.f

cpoly3<-function(p){
#
con1 = p[3] / (p[2] * (p[2]-p[1]))
con2 = p[5] / (p[4] * (p[4]-p[1]))
#
b<-rep(0,3)
b[3] = (con1-con2) / (p[2]-p[4])
b[2] = con1 - b[3] * (p[1]+p[2])
b[1] = p[1] * (p[2]*b[3] - con1)
return(b)                
}
               