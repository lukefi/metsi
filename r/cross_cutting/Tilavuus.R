volume <- function(hkanto, dbh, height, coeff) {

    # oletuksena on kutsussa oleva uudelleen estimoitu malli
    # Joken aivan alkuperäiset mallit varalta tässä
    #        if (sp=="pine") coef <- c(2.1288,-0.63157,-1.6082,2.4886,-2.4147,2.3619,-1.7539,1.0817)
    #        if (sp=="spruce") coef<-c(2.3366,-3.2684,3.6515,-2.2608,0.0,2.1501,-2.7412,1.8876)
    #        if (sp=="birch") coef<-c(0.93838,4.1060,-7.8517,7.8993,-7.5018,6.3863,-4.3918,2.1604)

    # runkokäyrässä on oletuksena korjattu malli, jossa
    # oletusläpimitta on dbh
    # lasketaan tilavuus 10 cm pätkissä kannonkorkeudesta alkaen
    h <- seq(hkanto, height, 0.1)
    if (h[length(h)] < height) h <- c(h, height)

    # tilavuus runkokäyrällä
    v_piece <- rep(0, (length(h) - 1))
    # pölkkyjen latvaläpimitat
    d_piece <- dhat(h[-1], height, coeff)
    # tilavuus integroimalla
    for (j in 1:length(v_piece)) {
        vp <- integrate(ghat, h[j], h[j + 1], height = height, coef = coeff)$value # ghat from Runkokäyräennusteet.R
        v_piece[j] <- vp
    }
    # vain palan latvan korkeus
    h_piece <- h[-1]
    v_cum <- cumsum(v_piece)
    vol <- round(sum(v_piece) * 1000, 3)
    list(vcum = v_cum, dpiece = d_piece, hpiece = h_piece, v = vol)
}
