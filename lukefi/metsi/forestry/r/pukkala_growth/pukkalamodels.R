## Lauri Mehtätalo 2022 (Based on scripts from Mikko Peltoniemi)
## Pukkala et al., 2021 models
## https://academic.oup.com/forestry/advance-article/doi/10.1093/forestry/cpab008/6172082
#malli<-"Pukkala2021"
malli<-"PukkalaLappi1320"
library(lmfor)
source("menu/hdmod.R")
#volMods <- readRDS("tilavuusmalli/vol_mods_final_LM.rds")
data(vol_mods)
volMods<-vol_mods
setwd("pukGrowth")
source("growthfuncs.R")
library(Matrix)
library(VGAM)

# LM 16.3.2022. Sisäänkasvun malleissa kasvupaikkojen koodauksessa on jotain häikkää,
# varmistettava Mikolta/Timolta onko koodattu oikein.
# Pukkalan artikkelissa on erikseen muuttujat "Sub-xeric" ja "Sub-xeric or poorer"
# mikko koodannut jälkimmäisen "CT-".

### Test, Motti Asikkala, 1st simulations, TaimiCO2
#dt <- read.table("dt.txt",header=TRUE)
#dt <- cbind(dt[, c("simulointi", "vuosi","puulaji","LPM","Runkoluku")],sitetype=2,landclass=1,TS=1400,
#       yk=7000,xk=500,alt=120,harv=0)
#names(dt)[c(3,4,5)]<-c("sp","dbh","Ntrees")
## dtin: 1 sp, 2 dbh, 3 N, 4 sitetype, 5 landclass, 6 TS
#dtin <- dt[dt$simulointi==1 & dt$vuosi == 17, -c(1:2)] # 36 puuta alkuhetkellä.
#dtin$y<-1
#dtin$yr<-0
#dtin$id<-1:nrow(dtin)
#dtinma<- dtinko<-dtinku<-dtinorig <- dtin
#dtinma$sitetype<-3
#dtinma$sp<-1
#dtinko$sitetype<-3
#dtinko$sp<-3
#
#print(date())
#dtin$yr<-0
#dtin$id<=1:nrow(dtin)
#dtinku<-dtin
#dtinma$yr<-0
#dtinma$id<-(1:nrow(dtinma))
#dtinko$yr<-0
#dtinko$id<-1:nrow(dtinko)
#
#dtinku<-predheight(dtinku,model=2)
#dtinku<-predvol(dtinku)
#dtinma<-predheight(dtinma,model=2)
#dtinma<-predvol(dtinma)
#dtinko<-predheight(dtinko,model=2)
#dtinko<-predvol(dtinko)
#write.table(dtinma,"dtinma.txt")
#write.table(dtinku,"dtinku.txt")
#write.table(dtinko,"dtinko.txt")
#
#if (malli==2021) {
#  id<-read.table("pukkalaid2021.txt",header=TRUE)
#  surv<-read.table("pukkalasurv2021.txt",header=TRUE)
#  ing<-read.table("pukkalaing2021.txt",header=TRUE)
#  attr(ing,"alpha")<-c(3,3,3,3)
#  zi<-read.table("pukkalazi2021.txt",header=TRUE)
#  } else if (malli==2013) {
#  id<-read.table("pukkalaid2013.txt",header=TRUE)
#  surv<-read.table("pukkalasurv2013.txt",header=TRUE)
#  ing<-read.table("lappipukkalaing2020.txt",header=TRUE)
#  attr(ing,"alpha")<-c(3.19,2.28,2.57)
#  zi<-read.table("lappipukkalazi2020.txt",header=TRUE)
#  }



dtinma<-dtinma0<-read.table("dtinma.txt",header=TRUE)
dtinku<-dtinku0<-read.table("dtinku.txt",header=TRUE)
dtinko<-dtinko0<-read.table("dtinko.txt",header=TRUE)


#pdf("mannikkoKokojak.pdf")
nper<-30
resku<-dtinku
resma<-dtinma
resko<-dtinko
for (i in 1:nper) {
    dtinku<-grow(dtinku,model=malli)
    dtinku<-predheight(dtinku,model=2)
    dtinku<-predvol(dtinku)
    resku<-rbind(resku,dtinku)
    dtinma<-grow(dtinma,model=malli)
    dtinma<-predheight(dtinma,model=2)
    dtinma<-predvol(dtinma)
#    plot(dtinma$dbh,dtinma$Ntrees,type="h",col=dtinma$sp,xlim=c(0,50),ylim=c(0,1100))
    resma<-rbind(resma,dtinma)
    dtinko<-grow(dtinko,model=malli)
    dtinko<-predheight(dtinko,model=2)
    dtinko<-predvol(dtinko)
    resko<-rbind(resko,dtinko)
    }
print(date())
#dev.off()

# Ennusta puille pituudet
# Mehtätalon 2004 pituusmallin parametrien arvot kullakin ajan hetkellä ja kullekin puulajille

pdf(paste("standdat",malli,".pdf",sep=""))
par(mfcol=c(2,2))
a<-standDat(resma)
b<-standDat(resku)
c<-standDat(resko)
mot<-standDat(dt)
dev.off()

resku<-resku[resku$Ntrees>1,]
resko<-resko[resko$Ntrees>1,]
resma<-resma[resma$Ntrees>1,]

save(resku,resko,resma,file=paste("respuk",malli,".RData",sep=""))

pdf(paste("kehitys",malli,".pdf",sep=""))
par(mfrow=c(2,2))
linesplot(resku$yr,resku$dbh, resku$id,main="kuvauspuiden dbh, OMT-kuusikko",col.lin=resku$sp,xlab="aika",ylab="d, cm")
linesplot(resma$yr,resma$dbh, resma$id,main="kuvauspuiden dbh, MT-mannikko",col.lin=resma$sp,xlab="aika",ylab="d, cm")
linesplot(resko$yr,resko$dbh, resko$id,main="kuvauspuiden dbh, MT-koivikko",col.lin=resko$sp,xlab="aika",ylab="d, cm")

plot(seq(0,5*nper,5),tapply(resku$v*resku$Ntrees/1000,resku$yr,sum),main="Kokonaistilavuus, OMT-kuusikko")
plot(seq(0,5*nper,5),tapply(resma$v*resma$Ntrees/1000,resma$yr,sum),main="Kokonaistilavuus, MT-mannikko")
plot(seq(0,5*nper,5),tapply(resko$v*resko$Ntrees/1000,resko$yr,sum),main="Kokonaistilavuus, MT-koivikko")

plot(seq(0,5*nper,5),tapply(pi*resku$dbh^2/40000*resku$Ntrees,resku$yr,sum),main="KokonaisPPA, OMT-kuusikko"); abline(h=1.85)
plot(seq(0,5*nper,5),tapply(pi*resma$dbh^2/40000*resma$Ntrees,resma$yr,sum),main="KokonaisPPA, MT-mannikko"); abline(h=1.85)
plot(seq(0,5*nper,5),tapply(pi*resko$dbh^2/40000*resko$Ntrees,resko$yr,sum),main="KokonaisPPA, MT-koivikko"); abline(h=1.85)

plot(seq(0,5*nper,5),tapply(resku$Ntrees*(resku$dbh>0),resku$yr,sum),main="Kokonaisrulu, OMT-kuusikko")
plot(seq(0,5*nper,5),tapply(resma$Ntrees*(resma$dbh>0),resma$yr,sum),main="Kokonaisrulu, MT-mannikko")
plot(seq(0,5*nper,5),tapply(resko$Ntrees*(resko$dbh>0),resko$yr,sum),main="Kokonaisrulu, MT-koivikko")
dev.off()


windows()
par(mfcol=c(2,2))
for (i in 1:4) linesplot(resma$dbh[resma$sp==i],resma$h[resma$sp==i],resma$yr[resma$sp==i],col.lin=i)
windows()
par(mfcol=c(2,2))
for (i in 1:4) linesplot(resku$dbh[resku$sp==i],resku$h[resku$sp==i],resku$yr[resku$sp==i],col.lin=i)
windows()
par(mfcol=c(2,2))
for (i in 1:4) linesplot(resko$dbh[resko$sp==i],resko$h[resko$sp==i],resko$yr[resko$sp==i],col.lin=i)

pdf("pituuksia.pdf")
par(mfcol=c(2,2))
for (i in seq(0,5*nper,5)) linesplot(resma$dbh[resma$yr==i],resma$h[resma$yr==i],resma$sp[resma$yr==i],col.lin=resma$sp[resma$yr==i],xlim=c(0,80),ylim=c(0,25),cex=resma$Ntrees[resma$yr==i]/100)
for (i in seq(0,5*nper,5)) linesplot(resku$dbh[resku$yr==i],resku$h[resku$yr==i],resku$sp[resku$yr==i],col.lin=resku$sp[resku$yr==i],xlim=c(0,80),ylim=c(0,25),cex=resku$Ntrees[resku$yr==i]/100)
for (i in seq(0,5*nper,5)) linesplot(resko$dbh[resko$yr==i],resko$h[resko$yr==i],resko$sp[resko$yr==i],col.lin=resko$sp[resko$yr==i],xlim=c(0,80),ylim=c(0,25),cex=resko$Ntrees[resko$yr==i]/100)
dev.off()

resma2<-resma[resma$yr==5,c("dbh","h","Ntrees")]


