library_requirements <- c("lmfor", "stats4")
if(!all(library_requirements %in% installed.packages()[, "Package"]))
  install.packages(repos="https://cran.r-project.org", dependencies=TRUE, library_requirements)

library(stats4)
library(lmfor)

winit<-function(d,minf=1e-6) {
       s<-sd(d)
       if (is.na(s)) s<-0.1
       shape<-20/s
       scale<-mean(d)
       while (min(dweibull(d,shape,scale))<minf) shape<-0.99*shape
       c(shape=shape,scale=scale)
       }


# Tässä lasketaan skaalaustermi analyyttisesti paitsi 
# alle 4.5 cm:n puille se integroidaan numeerisesti.
# Yo funktiossa sama lasketaan kokonaan numeerisesti,
# jolloin funktiota on helpompi yleistää muihin tilanteisiin.                   
dVMIweib<-function(d,shape,scale,q=1.5,r1=5.64,r2=9.00,d1=4.5,d2=9.5) {
                    f<-d^2*dweibull(d,shape,scale)
                    f[d>=d1]<-q*(100*r1/50)^2*dweibull(d[d>=d1],shape,scale)
                    f[d>=d2]<-q*(100*r2/50)^2*dweibull(d[d>=d2],shape,scale)
                    EW<-integrate(function(x) x^2*dweibull(x,shape,scale),0,d1)$value+
                        (pweibull(d2,shape,scale)-pweibull(d1,shape,scale))*q*(100*r1/50)^2+
                        (1-pweibull(d2,shape,scale))*q*(100*r2/50)^2
                    f/EW
                    }


nll.recml.VMI<-function(d,lshape,D,Dtype,trace=FALSE,minshape=0.01,q=1.5,r1=5.64,r2=9.00,d1=4.5,d2=9.5) {  
	shape<-exp(lshape)+minshape
	if (Dtype=="A") {
		scale<-scaleDMean1(D,shape)
	} else if (Dtype=="B") {
		scale<-scaleDGMean1(D,shape)
	} else if (Dtype=="C") {
		scale<-scaleDMed1(D,shape)
	} else if (Dtype=="D") {
		scale<-scaleDGMed1(D,shape)
	} else stop("Dtype should be any of 'A', 'B', 'C', 'D'")
    if (trace) cat(shape,scale," ")
	nll<-try(-sum(log(dVMIweib(d,shape,scale,q,r1,r2,d1,d2))),silent=TRUE)
	if (class(nll)=="try-error") nll<-Inf
	if (trace) cat(nll,"\n")
	attributes(nll)<-list(parms=c(shape=shape,scale=scale))
	nll
}

fitRMLVMI2<-function(d,D,Dtype,init=NA,trace=FALSE,minshape=0.05,q=1.5,r1=5.64,r2=9.00,d1=4.5,d2=9.5) {
             if (is.na(init[1])) init<-winit(d)[1]
             linit<-log(init-minshape)
             nll<-function(lshape) nll.recml.VMI(d,lshape,D,Dtype,trace,minshape,q,r1,r2,d1,d2)   
             if (all(D==d)) {
                est1<-nll(3)
                } else { 
                fail<-Inf
                attr(fail,"coef")<-c(NA,NA)
                estim<-function(ini) {
                       est<-try(mle(nll,start=list(lshape=ini)))
                       if (class(est)=="try-error") {
                          est<-fail 
                          } else {
                          est<-nll(coef(est))
                          }
                       }
                est1<-lapply(linit,estim)
                est1<-est1[unlist(est1)==min(unlist(est1))][[1]]
                }
             est1
             }

fitRMLVMI<-function(d,D,Dtype,init=NA,trace=FALSE,minshape=0.01,q=1.5,r1=5.64,r2=9.00,d1=4.5,d2=9.5,shdef=1) {
             if (is.na(init)) init<-winit(d)[1]
             linit<-log(init-minshape)
             nll<-function(lshape) nll.recml.VMI(d,lshape,D,Dtype,trace,minshape,q,r1,r2,d1,d2)   
             if (length(d)==0) {
                est1<-log(shdef-minshape)
                } else if (all(D==d)) {
                est1<-3
                } else { 
                est1<-try(coef(mle(nll,start=list(lshape=linit))),silent=TRUE)
                if (class(est1)=="try-error") est1<- -1000
                }
             sol<-nll(est1)
             }
           
Hpred<-function(lpuut,kpuut,malli,m) {
        lpuut$Y<-1    
        muLp<-predict(malli,newdata=lpuut,level=0)    
        ZLp<-model.matrix(malli$modelStruct$reStruct,data=lpuut)  
        D<-getVarCov(malli)
        sigma<-malli$sigma
        delta<-attr(malli$apVar,"Pars")[4]
        varFix<-sigma^2*log(lpuut$HGM/lpuut$DGM+2)^(2*delta)+diag(ZLp%*%D%*%t(ZLp))
        predHFix<-lpuut$lpm^m/muLp^m+1.3
        predHFixBC<-predHFix+0.5*m*(m+1)*lpuut$lpm^m/muLp^(m+2)*varFix
        lpuut$predHFix<-predHFix
        lpuut$predHFixBC<-lpuut$pred<-predHFixBC
        if (nrow(kpuut)>0) {
           kpuut$Y<-1
           mu<-predict(malli,newdata=kpuut,level=0)
           y<-kpuut$lpm/(kpuut$height-1.3)^(1/m)
           Z<-model.matrix(malli$modelStruct$reStruct,data=kpuut)
           R<-sigma^2*log(kpuut$HGM/kpuut$DGM+2)^(2*delta)
           if (length(R)>1) R<-diag(R)
           b<-D%*%t(Z)%*%solve(Z%*%D%*%t(Z)+R)%*%(y-mu)
           varb<-D-D%*%t(Z)%*%solve(Z%*%D%*%t(Z)+R)%*%Z%*%D
           # ennustet lukupuille     
           muPlusbLp<-muLp+ZLp%*%b
           varFixRan<-sigma^2*log(lpuut$HGM/lpuut$DGM+2)^(2*delta)+diag(ZLp%*%varb%*%t(ZLp))
           predHFixRan<-lpuut$lpm^m/muPlusbLp^m+1.3
           predHFixRanBC<-predHFixRan+0.5*m*(m+1)*lpuut$lpm^m/muPlusbLp^(m+2)*varFixRan
           lpuut$predHFixRan<-predHFixRan
           lpuut$predHFixRanBC<-lpuut$pred<-predHFixRanBC 
           }
        lpuut
        }
        

# Sisään menee ositerivi (yhden rivin data.frame) ja ositteen puut sisältävä data frame. 
# Ositerivissä on oltava ainakin seuraavat muuttujat
# DGM - ppa-mediaanipuun läpimitta
# HGM - ppa-mediaanipuun pituus 
# G - kokonaisppa m2/ha
# Gos - ositteen PPA m2/ha
# DDY - lämpösumma
# spe - ositteen puulaji
# Puutiedoissa on oltava
# lpm - puiden läpimitat, cm
# height - koepuiden mitatut pituudet metreinä (lukupuille height=NA)
# Lisäksi annetaan argumenttina
# n - kokonaisluku, montako kuvauspuuta halutaan
# tapa - miten kuvauspuut poimitaan: "dcons" vako läpimittaluokan leveys 
#                                    "fcons" vakio luokan runkoluku
# HDmod - Siipilehdon ja kankaan pituusmallit listana järjesteyksessä mä, ku, ko
# hmalli - kokonaisluku, minkä puulajin pituusmallia ositteelle käytetään (1, 2 tai 3)

generoi.kuvauspuut<-function(ositerivi,lukupuut,path="",n=10,tapa="dcons",hmalli=1) {
   # kokojakauma
   if (!exists("HDmod")) {
      load(paste0(path,"HDmod_Siipilehto_Kangas_2015",".RData"))
   }

   sol<-fitRMLVMI(lukupuut$lpm,ositerivi$DGM,Dtype="D",init=0.5,trace=FALSE,minshape=0.055)
   theta<-attr(sol,"parms")
   Nos<-40000/pi*ositerivi$Gos/(theta[2]^2*gamma(2/theta[1]+1)) # ositteen runkoluku
   if (tapa=="dcons") {
      dlim <- seq(qweibull(1e-8,theta[1],theta[2]),qweibull(1-1e-8,theta[1],theta[2]),length=n+1)
      } else if (tapa=="fcons") {
      dlim <- qweibull(seq(1e-8,1-1e-8,length=n+1),theta[1],theta[2])
      }
   kuvauspuut<-merge(cbind(ositerivi,osite=1),data.frame(lpm=(dlim[-1]+dlim[-(n+1)])/2,                  # kuvauspuiden läpimitat
                                lkm=Nos*diff(pweibull(dlim,theta[1],theta[2])), # kuvauspuiden edustamat runkoluvut
                                osite=1))
   if (!all(is.na(lukupuut$height))) {
      koepuut<-merge(cbind(ositerivi,osite=1),cbind(lukupuut[!is.na(lukupuut$height),],osite=1))
      } else {
      koepuut<-lukupuut[!is.na(lukupuut$height),]
      }
   kuvauspuut$h <- Hpred(kuvauspuut,koepuut,malli=HDmod[[hmalli]],m=c(2,3,2)[hmalli])$pred  # kuvauspuiden pituudet
   kuvauspuut
   }
   
