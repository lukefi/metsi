# Tämä ohjelma esittää, miten R-aliohjelmia käytetään
# tehty 28.02.2022 Annika Kangas
# Esimerkki runkokäyrien soveltamiseen
# Tarvittavat aliohjelmat

setwd("C:/menu/additional-content/annika_kangas_apteeraus")
source("ApteerausNäsberg.R")
source("Runkokäyräennusteet.R")
source("Tilavuus.R")
source("Runkokäyrän korjausmalli.R")
source("Korjauskertoimet.R")

# luetaan tarvittavat taulukot tässä
# mallien kertoimet ovat tässä rds-tiedostossa
models_pine <- readRDS("pine taper curve.rds")
models_spruce <- readRDS("spruce taper curve.rds")
models_birch <- readRDS("birch taper curve.rds")
# josta ne voi lukea tavalliseksi vektoriksi
# Laasasenahon malli "climbed", VAPU-aineistosta malli "felled"
# TLS aineistosta malli "scanned"

# puutavaralajien määrittelyt apteerausta varten taulukko
P<-read.table("Puutavaralajimäärittelyt.txt")
# m -- number of timber assortment price classes, integer
m<-length(P[,1]) 
#    div -- tree stem divisor (segment length), double
div<-10 # 10 cm segmentit

sps<-c("pine","spruce","birch")
coef <- vector("list",length(sps)) #preallocate a vector into which coefs are read into
names(coef) <- sps
coef[["pine"]]<-models_pine[["climbed"]]$coefficients
coef[["spruce"]]<-models_spruce[["climbed"]]$coefficients
coef[["birch"]]<-models_birch[["climbed"]]$coefficients

#esimerkkipuu
hkanto<-0.1
dbh<-30
# testiä varten oletetaan myös d6 tunnetuksi
# d6<-20
# d20p oletetaan olevan tuntematon, 
# ja lasketaan iteratiivisesti kuten C Snellman ohjelmassa 
height<-25
sp<-"pine"

# vaihe 1. lasketaan runkokäyrän korjausmalli Joukon vanhalla mallilla
# ts. tätä ei ole vielä laskettu uudestaan uudesta aineistosta
# tilanteisiin, joissa d6 tunnettu, tarvitaan oma korjausmalli
# ensin korjausyhtälön pisteet
p<-tapercurvecorrection1(dbh,height,sp)
#sitten itse kertoimet
b<-cpoly3(p)
# ja lopuksi uudet kertoimet
coefnew<-coef[[sp]]
for (i in 1:3){
# korjausmallilla vaikutetaan kolmeen ensimmäiseen kertoimeen
    coefnew[i]<-coefnew[i]+b[i]
}

# vaihe 2,  lasketaan ennuste 20% läpimitalle ennustetun runkokäyrän pohjalta
# c on suhde dx/d20 tai dx/d80 latvasta katsoen 
# jolloin d20=dx/c
# käytännössä d20=d13/c, jossa c on suhde d13/d20
hx<-1.3
c<-crkt(hx,height,coefnew)
d20<-dbh/c
# kun kerrotaan alkuperäinen runkokäyrämalli d20:n ennusteella,
# saadaan runkokäyrämalli, joka ennustaa läpimitan tietyllä korkeudella
# läpimitan funktiona
coefnew<-coefnew*d20

# vaihe 3. lasketaan tilavuus integroimalla runkokäyrää

vhat<-volume(hkanto,dbh,height,coefnew)
vhat$v

# vaihe 4. muodostetaan puutason lähtötiedot apteeraukseen
# n -- number of tree segments, integer
n<-(height*100)/div-1

# T -- tree stem profile as a 2-dimensional array of size n x 3
T<-array(data=NA,dim=c(n,3),dimnames=NULL)
T[,1]<-vhat$dpiece*10 #diameter at the end of piece in mm
T[,2]<-vhat$hpiece #height at the end of each piece
T[,3]<-vhat$vcum #cumulative volume by pieces

# Apteerausaliohjelman kutsu
Apt<-apt(height,T,P,m,n,div)
Apt$volumes
Apt$values
