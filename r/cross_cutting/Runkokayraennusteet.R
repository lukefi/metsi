crkt<-function(h,height,coef){
    # olkoon hx pisteen x etäisyys maanpinnan tasosta (hx:n laatu: m).
    # funktio laskee suhteen  dx / d80  missä dx on läpimitta pisteessä x    
    # ja d80 on läpimitta pisteessä, jonka etäisyys latvasta on 0.8*h.
    # x = 1-h/height = (height-h)/height    
    # Snellman alkuperäinen koodi crkt.f!
    x<-(height-h)/height
    crkt<-x*coef[1]+x^2*coef[2]+x^3*coef[3]+x^5*coef[4]+
        x^8*coef[5]+x^13*coef[6]+x^21*coef[7]+x^34*coef[8]
}

dhat<-function(h,height,coef){
    # oletus on, että malli on korjattu korjausmallilla
    # jolloin käytetty d on dbh  ja f = d20hat*fb (Laasasenaho 33.3)
    # ja malli antaa suoraan läpimitan
    x<-(height-h)/height
    dhat<-x*coef[1]+x^2*coef[2]+x^3*coef[3]+x^5*coef[4]+
        x^8*coef[5]+x^13*coef[6]+x^21*coef[7]+x^34*coef[8]
    
}

ghat<-function(h,height,coef){
#lasketaan suhteellinen läpimitta korkeudella hx
# x on suhteellinen korkeus latvasta
    x<-(height-h)/height
    d<-x*coef[1]+x^2*coef[2]+x^3*coef[3]+x^5*coef[4]+
        x^8*coef[5]+x^13*coef[6]+x^21*coef[7]+x^34*coef[8]
    # oletus on, että malli on korjattu korjausmallilla 
    # jolloin käytetty d on dbh ja f = d20hat*fb (Laasasenaho 33.3)
    # ja d on suoraan läpimitta
    d<-d/100
    ghat<-(d^2)*pi/4
}

