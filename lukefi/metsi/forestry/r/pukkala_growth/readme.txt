Pukkalan kasvumallit, r-implementointi.

Varsinaiset mallit on R-objekteissa PukkalaLappi1320.rds ja Pukkala2021.rds.
Kasvuennuste tehdään functiolla grow.

Funktion argumentit
dtin: data.frame; kuvauspuut
model: merkkijono; kertoo minkä nimisessä tiedostossa mallit ovat, ilman tunnistetta rds.
path: merkkijono; polku hakemistoon, jossa mallitiedostot ovat
perlength: numeerinen; kasvujakson pituus. En suosittele käyttämään muita kuin kokonaislukuja väliltä 1,...,5.
standArea: metsikön pinta-ala neliömetreinä.

palautusarvo: data ftrame, samaa muotoa kuin dtin. Päivitetty kuvauspuden läpimitat,
              runkoluvut ja iät sekä lisätty rivit kasvujakson aikana syntyneille
              uusille puille.

pituudet voidaan lisätä jälkikäteen Mehtätalon pituusmalleilla kyttäen funktiota predheight.
funktio saa argumenttiaan samanmuotoisen kuvauspuudatan kuin funktio grow ja palauttaa
datan johon on lisätty sarakkeeseen h kuvauspuiden pituudet metreinä. Jos ko. sarake tälon jo olemassa,
funktio ylikirjoittaa pituudet siihen.

kuvauspuudataframen muuttujat (tähdellä merkittyjä tarvitaan vain pituuksien laskennassa)
id: puun kokonaisluvullinen tunniste
sp: numeerinen; puulaji. 1=mänty, 2=kuusi, 3=rauduskoivu, 4=hieskoivu, 5=haapa, 6=leppä, 7=muu
dbh: numeerinen, läpimitta, cm
Ntrees: numeerinen, kuvauspuun edustama runkoluku 1/ha.
sitetype: numeerinen kasvupaikka: 1=lehto, 2=lehtomainen kangas, 3=tuore kangas, 4=kuivahko kangas, 5=kuiva kangas, 6=karukkokangas ym
landclass: numeerinen: 1=kangas, >1=suo
TS: numeerinen, lämpösumma
yk: numeerinen, koealan y-koordinaatti yhtenäiskoordinaatiostossa
xk: numeerinen, koealan x-koordinaatti*
alt: korkeus meren pinnasta*
harv: numeerinen, saa arvon 1 jos metsää on harvennettu edeltävän 5 vuoden aikana, muuten 0*
yr: vuosi, numeerinen (voi olla kalenterivusi tai metsikön ikä).
