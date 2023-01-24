## Lauri Mehtätalo 2022 (Based on scripts from Mikko Peltoniemi)

library_requirements <- c("Matrix", "VGAM")
if(!all(library_requirements %in% installed.packages()[, "Package"]))
  install.packages(repos="https://cran.r-project.org", dependencies=TRUE, library_requirements)

library(Matrix)
library(VGAM)

# Computes the basal area of larger trees for each tree of data frame dtin
# for all trees and by species (BAL, BAlp, BALs, BALh)
# and the basal area for all trees and by species (G,Gp, Gs, Gh)
# returns a data frame augmented by these variables.
BALGf <- function(dtin) {
    # Laskee annetulle puulle x sitä suurempien puiden ppa:t
    # jaettuna arvolla sqrt(d+1)
    dtin2<-cbind(dtin,ord=1:nrow(dtin)) # alkuperäinen järjestys
    dtin2<-dtin2[order(dtin2$dbh,decreasing=TRUE),]
    n<-nrow(dtin2)
    ones<-matrix(1,ncol=n,nrow=n)
    ones[lower.tri(ones, diag = TRUE)]<-0
    onespine<-onesspruce<-onesdeci<-ones
    onespine[dtin2$sp!=1,]<-0
    onesspruce[dtin2$sp!=2,]<-0
    onesdeci[dtin2$sp<=2,]<-0
    ba<-pi*dtin2$dbh^2/40000*dtin2$Ntrees
    dtin2$G=sum(ba)
    dtin2$Gp=sum(ba[dtin2$sp==1])
    dtin2$Gs=sum(ba[dtin2$sp==2])
    dtin2$Gh=sum(ba[dtin2$sp>=3])
    dtin2$SD<-sqrt(sum(dtin2$dbh^2*dtin2$Ntrees)/sum(dtin2$Ntrees)-(sum(dtin2$dbh*dtin2$Ntrees)/sum(dtin2$Ntrees))^2)
    dtin2$BAL=t(ba%*%ones)
    dtin2$BALp=t(ba%*%onespine)
    dtin2$BALs=t(ba%*%onesspruce)
    dtin2$BALh=t(ba%*%onesdeci)
    dtin2<-dtin2[order(dtin2$ord),]
    dtin2[,-(1:ncol(dtin2))[names(dtin2)=="ord"]]
    }

## Grow
# Kasvattaa puita annetulla mallilla
# Mallin kertoimet annetaan data.framena, jossa rivien nimet
# on kirjattu siinä muodossa että niistä voidaan muodostaa R:n
# mallifunktioiden ymärtämä formula.
# Kaikki malleissa esiintyvät muuttujat pitää olla data framessa dtin.
# Sisäänkasvut generoidaan aina negatiivisesta binomijakaumsata
grow <- function(dtin, model="Pukkala2021",
                 path="",perLength=5,standArea=10000) {
  m<-readRDS(paste(path,model,".rds",sep=""))
#  betaid<-read.table(paste(path,model[1],".txt",sep=""))
#  betaing<-read.table(paste(path,model[2],".txt",sep=""))
#  attr(ing,"alpha")<-read.table(paste(path,model[5],".txt",sep=""))
#  betazi<-read.table(paste(path,model[3],".txt",sep=""))
#  betasurv<-read.table(paste(path,model[4],".txt",sep=""))
  X<-dtin
  X$Period<-perLength
  X$A<-standArea
  X<-BALGf(X) # LAsketaan tämän hetken ppa:t ja kilpailumuuttujat
  sp<-X$sp # toistaiseksi vain kolme puulajia
  ddbh<-surv<-ing<-rep(NA,nrow(X))
  modid<-as.formula(paste(c("y  ~1",rownames(m$betaid)[-1]), collapse=" + "))
  modsurv<-as.formula(paste(c("y ~1",rownames(m$betasurv)[-1]), collapse=" + "))
  moding<-as.formula(paste(c("y ~1",rownames(m$betaing)[-1]), collapse=" + "))
  modzi<-as.formula(paste(c("y ~1",rownames(m$betazi)[-1]), collapse=" + "))
  for (i in unique(sp)) {
      ddbh[sp==i]<- exp(model.matrix(modid,X[sp==i,])%*%m$betaid[,i]) # betaid:ssa pitää olla puulajit järjestyksessä
      surv[sp==i]<- 1/(1+exp(-model.matrix(modsurv,X[sp==i,])%*%m$betasurv[,i]))
      }
  zi <- 1/(1+exp(-bdiag(rep(list(model.matrix(modzi,X[1,])),ncol(m$betazi)))%*%unlist(m$betazi)))
  ing <- exp(bdiag(rep(list(model.matrix(moding,X[1,])),ncol(m$betaing)))%*%unlist(m$betaing))
  ## Vaihtoehtoinen tapa ilman silmukkaa, isommalla datalla voi katsoa onko tämä nopeampi
  #ddbh1<- t(exp(X[, 1:13]%*%paramsin))[t(as.matrix(dtin[, .(sp==1, sp==2, sp>=3)]))]
  #surv1<- t(1/(1+exp(-X[, c(1:3, 5, 16, 6, 7, 12, 14, 15)]%*%paramsSin)))[t(as.matrix(dtin[, .(sp==1, sp==2, sp>=3)]))]
  n<-nrow(dtin)
  dtin$dbh<-dtin$dbh+ddbh*perLength/5
  dtin$Ntrees<-dtin$Ntrees*surv^(perLength/5)
  dtin$yr<-dtin$yr+perLength
  newtrees<-dtin[rep(1,length(ing)),]
  newtrees$sp<-1:length(ing)
  newtrees$Ntrees<-rzinegbin(1,size=1/attr(m$betaing,"alpha"),munb=as.numeric(ing),pstr0=as.numeric(zi))
  newtrees$dbh<-0
  newtrees$id<-seq(max(dtin$id)+1,by=1,length=length(ing))
  dtin<-rbind(dtin,newtrees)
  dtin
  }

# lisää annettuun dataan ennustetun pituuden Mehtätalon 2004, 2005 mallilla
predheight<-function(dat,model=2) {
    dg<-standChar(dat)
 #   fixed.par(1,2,dg[1],dg[3],dg[2],dg[4],t=NA,mt=dat$sitetype[1],yk=dat$yk[1],xk=dat$xk[1],dd=dat$TS[1],kmp=dat$alt[1],harv=0)
    dhpar<-list(pine=dh.param(pl=1,dgm=dg[1],dgmj=dg[3],g=dg[2],gj=dg[4],
                     mt=dat$sitetype[1],yk=dat$yk[1],xk=dat$xk[1],
                     dd=dat$TS[1],kmp=dat$alt[1],harv=dat$harv[1],malli=model),
                spruce=dh.param(pl=2,dgm=dg[1],dgmj=dg[5],g=dg[2],gj=dg[6],t=NA,
                     mt=dat$sitetype[1],yk=dat$yk[1],xk=dat$xk[1],
                     dd=dat$TS[1],kmp=dat$alt[1],harv=dat$harv[1],malli=model),
                pendu=dh.param(pl=3,dgm=dg[1],dgmj=dg[7],g=dg[2],gj=dg[8],t=NA,
                     mt=dat$sitetype[1],yk=dat$yk[1],xk=dat$xk[1],
                     dd=dat$TS[1],kmp=dat$alt[1],harv=dat$harv[1],malli=model),
                pube=dh.param(pl=4,dgm=dg[1],dgmj=dg[9],g=dg[2],gj=dg[10],t=NA,
                     mt=dat$sitetype[1],yk=dat$yk[1],xk=dat$xk[1],
                     dd=dat$TS[1],kmp=dat$alt[1],harv=dat$harv[1],malli=model))
    for (spec in unique(dat$sp)) dat$h[dat$sp==spec]<-ennusta.pituudet(dat$dbh[dat$sp==spec],dhpar[[spec]])
    dat
    }

predvol<-function(dat,model="scanned") {
    voldat<-data.frame(dbh=dat$dbh,h=dat$h,dataset=factor(model,levels=c("climbed","felled","scanned")),temp_sum=dat$TS/10)
    voldat$d<-0 # tarvitaan koska mallissa lambda on d
    dat$v<-0
    for (spec in unique(dat$sp[dat$dbh>0])) dat$v[dat$sp==spec&dat$dbh>0]<-attributes(predvff(voldat[dat$sp==spec&dat$dbh>0,],volMods[[3]][[min(spec,3)]]))$trees$volume
    dat
    }

standDat<-function(dat,plot=TRUE) {
    dat<-as.data.frame(dat)
    tmp<-function(yr) {
         this<-dat[dat$yr==yr,]
         c(standChar(this),
           sum(this$Ntrees),
           sum(this$Ntrees[this$sp==1]),
           sum(this$Ntrees[this$sp==2]),
           sum(this$Ntrees[this$sp==3]),
           sum(this$Ntrees[this$sp==4]),
           sum(this$Ntrees*this$v/1000),
           sum((this$Ntrees*this$v/1000)[this$sp==1]),
           sum((this$Ntrees*this$v/1000)[this$sp==2]),
           sum((this$Ntrees*this$v/1000)[this$sp==3]),
           sum((this$Ntrees*this$v/1000)[this$sp==4]))
           }
    res<-cbind(unique(dat$yr),t(sapply(unique(dat$yr),tmp)))
    colnames(res)<-c("yr","dtot","gtot","dma","gma","dku","gku","dko","gko","dmu","gmu",
                     "ntot","nma","nku","nko","nmu","vtot","vma","vku","vko","vmu")
    res<-as.data.frame(res)
    if (plot) for (i in 2:(dim(res)[2])) try(plot(res$yr,res[,i],main=names(res)[i]),silent=TRUE)
    res
}

# palauttaa dgm:n ja ppa:n; oletetaan että data on jo järjestetty nousevasti
dgmg<-function(dat) {
      if (nrow(dat)) {
         cs<-cumsum(dat$Ntrees*dat$dbh^2)
         c(d=min(dat$dbh[cs>(max(cs)/2-1e-10)]),
              g=pi*sum(dat$Ntrees*dat$dbh^2/40000))
         } else {
         c(d=NA,g=0)
         }
      }
# funktio laskee metsikkötunnukset kuvauspuiden avulla, puulajit 1, 2, 3+4
# datassa pitää olla sarakkeet dbh, Ntrees ja sp
# Puulaji pitää tarkistaa, nyt nelonen on kaikki muut ja kolmonen koivut
standChar<-function(dat) {
           dat<-dat[order(dat$dbh),]
           c(dgmg(dat),
             dgmg(dat[dat$sp==1,]),
             dgmg(dat[dat$sp==2,]),
             dgmg(dat[dat$sp==3,]),
             dgmg(dat[dat$sp>3,]))
           }
