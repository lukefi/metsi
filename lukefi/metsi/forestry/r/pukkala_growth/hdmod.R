# aliohjelma, joka laskee BLU-ennustimen pituusmallin parametreille
hdblup<-function(myy,y,Z,D,R) {
        nobs<-length(myy)
        npar<-dim(D)[1]
        Rinv<-solve(R)
        Dinv<-solve(D)
        ZRinv<-t(Z)%*%Rinv
        varb<-solve(ZRinv%*%Z+Dinv)
        b<-varb%*%ZRinv%*%(y-myy)
        list(b=b,varb=varb)
        }

# pituusmallin läpimitan uudelleenparametrisointi
dexf<-function(pl,d,dGm) {
     c<-lda<-rep(NA,length(d))
     lda[pl==2|pl==1]<-7
     lda[pl==3|pl==4]<-6
     c[pl==1]<-0.98227850+0.05753439*dGm
     c[pl==2]<-1.564
     c[pl==3|pl==4]<-1.809
     ((d+lda)^(-c)-(dGm+10+lda)^(-c))/((10+lda)^(-c)-(30+lda)^(-c))
     }
     
# laskee kiinteän osan parameterien arvot 
fixed.par<-function(pl,malli=1,dgm=NA,dgmj=NA,g=NA,gj=NA,t=NA,mt=NA,yk=NA,xk=NA,dd=NA,kmp=NA,harv=NA) {
       if (pl==2) {
               p3a<--0.06505856
               p4a<-0.99851886 
               if (malli==1) {
                  p1a<-1.3985687
                  p2a<-2.1521769
                  p1b<-0.384201
                  p2b<-0.0156562
               } else if (malli==2) {
                  p1a<-9.446202-0.000941*yk-0.001194*kmp+0.032426*(mt>=3)-0.001213*dd
                  p2a<-2.117574	
                  p1b<-0.655861-0.000281*dd
                  p2b<-0.017127
               } else if (malli==3) {
                  p1a<-8.389718-0.00081*yk-0.001015*kmp-0.000999*dd+0.004604*g+0.02126*harv+0.036698*(mt>=3)
                  p2a<-1.820619	
                  p1b<-0.646102-0.000262*dd-0.003046*g
                  p2b<-0.019583
               } else if (malli==4) {
                  p1a<-11.793533-0.001239*yk-0.001265*kmp-0.001375*dd+0.003689*g-0.00706*dgm+0.020952*harv+0.002275*t	
                  p2a<-1.919873	
                  p1b<-2.325772-0.000225*yk-0.000379*dd-0.003381*g+0.001279*t	
                  p2b<-0.016715
               } else if (malli==5) {
	          p1a<-11.8110364126-0.0012389541*yk-0.0012777673*kmp-0.0013946339*dd+
	             0.0035965689*g-0.0103177654*dgm+0.0201370498*harv+0.0022390793*t+0.0033237516*dgmj
	          p2a<-1.9344340435 
	          p1b<-2.3338139130-0.0002255762*yk-0.0003806692*dd-0.0033935310*g+0.0012799988*t
	          p2b<-0.0167294609
	       } else {
                  p1a<-p2a<-p3a<-p4a<-p1b<-p2b<-NA
	       }
           } else if (pl==1) {
               p3a<--0.104646
               p4a<-1.822845
               if (malli==1) {
                  p1a<-1.5520027
                  p2a<-1.6437916
                  p1b<-0.6156029+0.0009346*dgm^2
                  p2b<--0.027069	
               } else if (malli==2) {
                  p1a<-2.2834464-0.0001025*yk+0.0002042*xk-0.0004661*kmp-0.0371364*(mt==4)
                  p2a<-1.6314323
                  p1b<--0.0411265+0.0000917*yk+0.0009643*dgm^2
                  p2b<--0.0275098	
               } else if (malli==3) {
                  p1a<-1.6884225-0.0003007*kmp-0.0292658*(mt==4)-0.0056709*dgm+0.0085951*g+0.035682*harv	
                  p2a<-1.4701162
                  p1b<-0.5213539-0.0074229*g+0.000537*dgm^2
                  p2b<--0.0072925
               } else if (malli==4) {
                  p1a<-3.0253285+0.0024309*t-0.0001953*yk-0.0346256*(mt==4)-0.0120275*dgm+0.0076132*g+0.0347336*harv	
                  p2a<-1.4722525
                  p1b<-0.3147058+0.00143*t-0.0076018*g+0.0003006*kmp+0.0001621*dd+0.0005545*dgm^2
                  p2b<--0.0120992
               } else if (malli==5) {               
                  p1a<-3.0239254-0.0001947*yk+0.0024310*t+0.0076678*g-0.0118670*dgm-
                       0.0361004*(mt==4)+0.0353184*harv
                  p2a<-1.4639480
                  p1b<-0.3297189+0.0013011*t-0.0076492*g+0.0005839*dgm^2+0.0002835*kmp+0.0001544*dd+0.0056500*dgmj
                  p2b<--0.0181771
               } else {
                  p1a<-p2a<-p3a<-p4a<-p1b<-p2b<-NA
               }
           } else if (pl==3|pl==4) {
               p3a<--0.06371285  
               p4a<-0.59812891
               if (malli==1) {
                  p1a<-0.8240965
                  p2a<-2.4929562
                  p1b<-0.1416735
                  p2b<-0.0136911
               } else if (malli==2) {
                  p1a<-6.434169-0.000784*yk	
                  p2a<-2.453588	
                  p1b<--0.192975+0.000243*xk+0.000226*dd
                  p2b<-0.01322
               } else if (malli==3) {
                  p1a<--0.3919645+0.0008112*kmp+0.0012222*dd+0.0034889*g+0.026839*harv	
                  p2a<-2.2571149
                  p1b<-0.1484691
                  p2b<-0.013068
               } else if (malli==4) {
                  p1a<-7.435023-0.000934*yk+0.024809*harv-0.010751*dgm+0.002831*g+0.002194*t	
                  p2a<-2.544288	
                  p1b<--0.408905+0.001419*t+0.000455*dd+0.000553*kmp	
                  p2b<-0.009574
               } else if (malli==5) { 
                  p1a<-5.4215267158-0.0006431073*yk+0.0240218527*harv+0.0031522304*g-
                       0.0150364560*dgm+0.0152416522*dgmj 
                  p2a<-2.4454169807
                  p3a<--0.06371285  
                  p4a<-0.59812891
                  p1b<-0.1264700460+0.0115940105*dgmj
                  p2b<-0.0050067611              
               } else {
                  p1a<-p2a<-p3a<-p4a<-p1b<-p2b<-NA
               }
           } else {
               p1a<-p2a<-p3a<-p4a<-p1b<-p2b<-NA
           }
       list(p1a=p1a,p2a=p2a,p3a=p3a,p4a=p4a,p1b=p1b,p2b=p2b)
       }
       
# palauttaa satunnaisen osan parametriestimaatit (s.d. & korrelaatio)            
hd.random<-function(pl,malli=1) {                       
           if (pl==2) {
                par.mat<-matrix(c(0.10847129,0.09579999,0.269,0.01678192,0.0222712,-0.681,
	   			  0.08908269,0.08671114,0.592,0.01699073,0.02249938,-0.642,
	   			  0.08694651,0.08416058,0.698,0.01392381,0.02110327,-0.484,
	   			  0.08134674,0.07998769,0.657,0.01171128,0.02215713,-0.49,
	    			  0.08119965,0.07999249,0.653,0.01136547,0.02221839,-0.517),nrow=5,byrow=TRUE)

              } else if (pl==1) {
                par.mat<-matrix(c(0.14144552,0.08945328,0.282,0.02877617,0.02094152,-0.715,
				 0.13558817,0.08365338,0.388,0.02865999,0.02156975,-0.713,
				 0.12945351,0.07863949,0.624,0.02407185,0.01424257,-0.62,
				 0.1207166,0.0741844,0.567,0.02191861,0.01578231,-0.742,
				 0.12059684,0.07479689,0.567,0.02250427,0.01464848,-0.758),nrow=5,byrow=TRUE)
              } else if (pl==3|pl==4) {
                par.mat<-matrix(c(0.21158582,0.09046623,0.526,0.02616912,0.01516498,-0.085,
				  0.11519881,0.08598663,0.527,0.02166083,0.01257797,-0.705,
				  0.11678313,0.08925556,0.637,0.02185526,0.0137738,-0.503,
				  0.11167172,0.08485231,0.603,0.01836341,0.0146941,-0.879,
				  0.10594421,0.07691128,0.564,0.01935249,0.01177019,-0.832),nrow=5,byrow=TRUE)
              } else {
                  rpar<-matrix(rep(NA,30),nrow=5)
              }
           if (malli>=1&malli<=5) {
                 rpar<-par.mat[malli,]
              } else { 
                 rpar<-rep(NA,6)
              }
           }

# palauttaa varianssifunktion arvon
variance.function<-function(pl,malli=1,d) {
         if (pl==2) {
                vm<-matrix(c(0.40133809,-0.534113,0.40220177,-0.5348114,0.4021615,-0.5349812,0.40386341,-0.5367404,0.40401046,-0.5368951),nrow=2)
                var<-(vm[1,malli]*(pmax(d,7.5)^(vm[2,malli])))^2
            } else if (pl==1) {
                vm<-matrix(c(0.25846367,-0.3724136,0.25803084,-0.3716203,0.25872359,-0.3727385,0.25920784,-0.3737408,0.25967081,-0.3745219),nrow=2)
                var<-(vm[1,malli]*(pmax(d,4.5)^(vm[2,malli])))^2
            } else if (pl==3|pl==4) {
                vm<-matrix(c(0.29753751,-0.4534796,0.29857407,-0.4546159,0.29785016,-0.4536262,0.29745544,-0.4535788,0.29451542,-0.4493769),nrow=2)
                var<-(vm[1,malli]*(pmax(d,9.5)^(vm[2,malli])))^2
            } else {
                var<-rep(NA,length(d))
            }
         var
         }

# ennustaa satunnaisparametrien arvot metsikössä 
# kpuut on lista, joka sisältää muuttujat
# dgm,dgmj,g,gj,t,mt,yk,dd,kmp,harv,h,d
predict.random<-function(pl,malli=1,kpuut=c()) {
         if (dim(data.frame(kpuut))[1]>=1) {
            apu<-fixed.par(pl,malli,kpuut$dgm,kpuut$dgmj,kpuut$g,kpuut$gj,kpuut$t,
                           kpuut$mt,kpuut$yk,kpuut$xk,kpuut$dd,kpuut$kmp,kpuut$harv)
            avar<-(1-exp(apu$p3a*kpuut$dgm))^apu$p4a 
            myy<-apu$p1a+apu$p2a*avar+
                 -(apu$p1b+apu$p2b*kpuut$dgm)*dexf(pl,kpuut$d,kpuut$dgm) 
            stages.of.devel<-unique(kpuut$dgm)
            n.of.trees<-length(kpuut$d)
            y<-log(kpuut$h)
#            cat("myy: ",myy,"\n")
#            cat("log(h) ",y,"\n")
            dex<--dexf(pl,kpuut$d,kpuut$dgm)
            Z<-Zapu<-cbind(1,dex)
            for (i in 1:length(stages.of.devel)) {
                Zapu2<-Zapu
                Zapu2[kpuut$dgm!=stages.of.devel[i],]<-c(0,0)
                Z<-cbind(Z,Zapu2)
                }
            rand.var<-hd.random(pl,malli)
            D<-matrix(0,ncol=2+2*length(stages.of.devel),nrow=2+2*length(stages.of.devel))
            D[1,1]<-rand.var[1]^2
            D[2,2]<-rand.var[2]^2
            D[2,1]<-D[1,2]<-rand.var[1]*rand.var[2]*rand.var[3]
            for (i in 1:length(stages.of.devel)) {
                D[2*i+1,2*i+1]<-rand.var[4]^2
                D[2*i+2,2*i+2]<-rand.var[5]^2
                D[2*i+1,2*i+2]<-D[2*i+2,2*i+1]<-rand.var[4]*rand.var[5]*rand.var[6]
                }
            R<-variance.function(pl,malli,kpuut$d)
            if (length(R)>1) R<-diag(R)
#            print(R)
#            print(D)
#            print(myy)
#            print(y)
#            print(Z)
            apu<-hdblup(myy,y,Z,D,R)
#            print(apu)
            b<-apu$b
            varb<-apu$varb
            rownames(varb)<-colnames(varb)<-c("stand","stand",rep(stages.of.devel,each=2))
            } else {
            b<-c(0,0,0,0)
            rand.var<-hd.random(pl,malli)
            D<-matrix(0,ncol=2,nrow=2)
            D[1,1]<-rand.var[1]^2
            D[2,2]<-rand.var[2]^2
            D[2,1]<-D[1,2]<-rand.var[1]*rand.var[2]*rand.var[3]
            varb<-D
            rownames(varb)<-colnames(varb)<-rep("stand",2)
            stages.of.devel<-0
            }
            sel<-seq(3,2+2*length(stages.of.devel),2)
            list(stand.a=b[1],stand.b=b[2],time.a=b[sel],time.b=b[sel+1],st.of.dev=stages.of.devel,varb=varb)
         }

# funktio tuottaa metsikön H/D -käyrän parametrit A ja B 
# hetkellä st.of.dev käyttäen mitattuja pituuksia data.framesta kpuut
dh.param<-function(pl,dgm,dgmj=NA,g=NA,gj=NA,t=NA,mt=NA,yk=NA,xk=NA,dd=NA,kmp=NA,harv=NA,kpuut=c(),malli=1,kuva=FALSE) {
         fixed<-fixed.par(pl,malli,dgm,dgmj,g,gj,t,mt,yk,xk,dd,kmp,harv)
#         cat("fixed ",fixed$p1a,fixed$p2a,fixed$p1b,fixed$p2b,"\n")
         random<-predict.random(pl,malli,kpuut)
#         print(random$varb)
         avar<-(1-exp(fixed$p3a*dgm))^fixed$p4a
         fixedAB<-list(A=fixed$p1a+fixed$p2a*avar,B=fixed$p1b+fixed$p2b*dgm,st.of.dev=dgm,pl=pl)
#         cat("A, fixed: ",fixedAB$A,
#             "B, fixed: ",fixedAB$B,"\n")
         p1a<-fixed$p1a+random$stand.a
         p2a<-fixed$p2a
         p1b<-fixed$p1b+random$stand.b
         p2b<-fixed$p2b
         if (sum(random$st.of.dev==dgm)) {
	    p1a<-p1a+random$time.a[random$st.of.dev==dgm]
	    p1b<-p1b+random$time.b[random$st.of.dev==dgm]
	    }
#         cat("A, f+r: ",p1a+p2a*(1-exp(-0.06505856*dgm))^0.99851886,
#             "B, f+r: ",p1b+p2b*dgm,"\n")
#	 cat("fix+rand ",p1a,p2a,p1b,p2b,"\n")
         avar<-(1-exp(fixed$p3a*dgm))^fixed$p4a
         A<-p1a+p2a*avar
         B<-p1b+p2b*dgm
         rownames(random$varb)[1:2]<-colnames(random$varb)[1:2]<-1*dgm
         apu<-rownames(random$varb)==dgm
         varb<-random$varb[apu,apu]
         
         fixrandAB<-list(A=A,B=B,st.of.dev=dgm,pl=pl,varb=varb,malli=malli)
         if (kuva) {
           dapu<-seq(1,50,1)
           lines(dapu,ennusta.pituudet(dapu,fixrandAB),lwd=2,col="red")
           lines(dapu,ennusta.pituudet(dapu,fixedAB),lwd=2)
           if (length(kpuut)!=0) points(kpuut$d,kpuut$h,col=kpuut$aika/10+4,cex=2,pch=17)
           }
         fixrandAB
         }

# funktio ennustaa pituudet läpimitoille d       
ennusta.pituudet<-function(d,par) {
#         y<-pmax(1.4,exp(par$A-par$B*dexf(par$pl,d,par$st.of.dev)))
         Z<-cbind(1,dexf(par$pl,d,par$st.of.dev))
         if (dim(par$varb)[1]==4) Z<-cbind(Z,Z)
#         print(variance.function(par$pl,par$malli,d))
#         print(Z%*%par$varb%*%t(Z))
         vary<-variance.function(par$pl,par$malli,d)+diag(Z%*%par$varb%*%t(Z))
         y<-pmax(1.4,exp(par$A-par$B*dexf(par$pl,d,par$st.of.dev)+0.5*vary))
         }

# ennustaa puiden tilavuudet laasasenahon tilavuusmalleilla         
ennusta.tilavuus<-function(pl,d,h=0,malli=1) {
         pl2<-pl
         pl2[pl2>4|pl2<1]<-5
         if (malli==1) {
            pars<-matrix(c(-5.39417,3.48060,0.039884,-5.39934,3.46468,0.0273199,
                           -5.41948,3.57630,0.0395855,-5.41948,3.57630,0.0395855,
                           rep(NA,3)),ncol=3,byrow=TRUE)  
            exp(pars[pl2,1]+pars[pl2,2]*log(2+1.25*d)-pars[pl2,3]*d)
         
         } else if (malli==2) {
            pars<-matrix(c(0.036089,2.01395,0.99676,2.07025,-1.07209,
                           0.022927,1.91505,0.99146,2.82541,-1.53547,
                           0.011197,2.10253,0.98600,3.98519,-2.65900,
                           0.011197,2.10253,0.98600,3.98519,-2.65900,
                           rep(NA,5)),ncol=5,byrow=TRUE)
            pars[pl2,1]*d^pars[pl2,2]*pars[pl2,3]^d*h^pars[pl2,4]*(h-1.3)^pars[pl2,5]
            }
         }

# Examples
# one old sample tree from the time when DGM was 12cm, 
# and two sample trees from time when dgm was 18 cm were measured from a pine stand
# we want to predict height for diameters 1,2,...,40 at times when DGM =18 and DGM=22

# Predict parameters of a pine stand using only DGM as a predictor for two points in time:
# When the DGM was 18 and now that it is 22 cm
par18<-dh.param(pl=1,dgm=18)
par22<-dh.param(pl=1,dgm=22)

# create a vector of diameters 1, 2, 3, ..., 30 cm
d<-seq(1,30,1)

# predict heights for those diameters at the two points in time
h18<-ennusta.pituudet(d,par18)
h22<-ennusta.pituudet(d,par22)

# plot HD-curves for those points in time
plot(d,h22,type="l",ylim=c(0,20),lty="dashed")
lines(d,h18,type="l",col="red",lty="dashed")

# Then assume that three trees were measured for height:
# When DGM was 12, the height of a 10 cm tree was observed to be 10 meters.
# Later on, when DGM was 18 cm, the heights of trees with dbh of 15 and 13 cm were observed to be 13 and 14 meters, respectively. 
kpuut<-data.frame(dgm=c(12,18,18),d=c(10,15,13),h=c(10,13,14),
                  dgmj=NA,g=NA,gj=NA,t=NA,mt=NA,yk=NA,xk=NA,dd=NA,kmp=NA,harv=NA)

# Add those observations to the plot
points(kpuut$d,kpuut$h,col=c("blue","red","red"))                  

# predict parameters of HD-curve using the three trees and DGM
par18<-dh.param(pl=1,dgm=18,kpuut=kpuut)
par22<-dh.param(pl=1,dgm=22,kpuut=kpuut)

# make the predictions 
h18<-ennusta.pituudet(d,par18)
h22<-ennusta.pituudet(d,par22)

# Add calibrated (localized) H-D curve
lines(d,h22,col="black")
lines(d,h18,col="red")
