# Korjausyhtälöt
# erikseen silloin, jos on tiedossa d6
# nyt koodattu vain tapaus jossa d6 ei ole tiedossa
# VMItä varten tarvitaan molemmat
# Alkuperäinen koodi Snellman crkd.f

# Aliohjelma muodostaa p-vektorin d:n ja h:n avulla laskettavalle
# runkokäyrälle. Korjauspolynomi b on laskettava siten, että
#    b(0)    =  0         latva
#    b(p(1)) =  0         0.1*h
#    b(p(2)) =  p(3)      0.4*h
#    b(p(4)) =  p(5)      0.7*h
# d on rinnankorkeusläpimitta (cm). Koska b:n
# arvo rinnankorkeusläpimittapisteessä ei ole 0 voidaan (d20)
# laskea vasta runkokäyräkorjauksen jälkeen!


tapercurvecorrection1<-function(d,h,sp){
# lasketaan aluksi tarvittavat muuttujat:
  dh = d / (h-1.3)
  dh2 = dh^2
  dl = log(d)
  hl = log(h)
  d2 = d^2
#
# lasketaan peruskäyrän arvot t1, t4 ja t7 sekä korjaukset y1, y4 ja y7
# korkeuksilla 0.1*h, 0.4*h ja 0.7*h:
# tässä varmaan t="taper" eli suhteellinen läpimitta verrattuna d20:een?
  
if(sp=="pine"){
  t1 = 1.100553
  t4 = 0.8585458
  t7 = 0.5442665
  #
  y1 = 0.26222 - 0.0016245*d + 0.010074*h + 0.06273*dh -
  0.011971*dh2 - 0.15496*hl - 0.45333/h
  y4 = -0.38383 - 0.0055445*h - 0.014121*dl + 0.17496*hl + 0.62221/h
  y7 = -0.179 + 0.037116*dh - 0.12667*dl + 0.18974*hl
}
#
  if(sp=="spruce"){
  t1 = 1.0814409
  t4 = 0.8409653
  t7 = 0.4999158
  #
  y1 = -0.003133*d + 0.01172*h + 0.48952*dh - 0.078688*dh2 -
  0.31296*dl + 0.13242*hl - 1.2967/h
  y4 = -0.0065534*d + 0.011587*h - 0.054213*dh + 0.011557*dh2 +
  0.12598/h
  y7 = 0.084893 - 0.0064871*d + 0.012711*h - 0.10287*dh +
  0.026841*dh2 - 0.01932*dl
  }
#  
  if(sp=="birch"){
  t1 = 1.084544
  t4 = 0.8417135
  t7 = 0.4577622
  #
  y1 = 0.59848 + 0.011356*d - 0.49612*dl + 0.46137*hl -
    0.92116/dh + 0.25182/dh2 - 0.00019947*d2
  y4 = -0.96443 + 0.011401*d + 0.13870*dl + 1.5003/h +
    0.57278/dh - 0.18735/dh2 - 0.00026*d2
  y7 = -2.1147 + 0.79368*dl - 0.51810*hl + 2.9061/h +
    1.6811/dh - 0.40778/dh2 - 0.00011148*d2
  }
  #
  if(sp=="alnus"){
  t1 = 1.108743
  t4 = 0.8186044
  t7 = 0.4682397
  #
  y1 = -1.46153 + 0.0487415*d + 0.663667*dl - 0.827114*hl -
  0.00106612*d2 + 1.87966/h + 1.85706/dh - 0.467842/dh2
  y4 = -1.24788 - 0.0218693*dh2 + 0.496483*dl - 0.291413*hl +
  1.92579/h + 0.863274/dh - 0.183220/dh2
  y7 = -0.478730 - 0.104679*dh + 0.151028*dl + 0.882010/h +
  0.178386/dh
  }
  y1t = min(abs(y1),0.1)
  if(sign(y1t)!=sign(y1)){y1t<-y1t*-1}
  y4t = min(abs(y4),0.1)
  if(sign(y4t)!=sign(y4)){y4t<-y4t*-1}
  y7t = min(abs(y7),0.1)
  if(sign(y7t)!=sign(y7)){y7t<-y7t*-1}
  #
  # lasketaan p-vektori. korjaukset on laskettu oletuksella b(p(1)) = y1.
  # koska kuitenkin b(p(1)):n on oltava 0 on korjaukset tehtävä käyrälle
  # joka saadaan kertomalla oletuskäyrä luvulla (t1+y1)/t1:
  #
  p<-rep(0,5)
  p[1] = 0.9
  p[2] = 0.6
  p[3] = t1/(t1+y1) * (t4+y4) - t4
  p[4] = 0.3
  p[5] = t1/(t1+y1) * (t7+y7) - t7
  return(p)
}
