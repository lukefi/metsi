apt <- function(T, P, m, n, div) {

    # Initialize arrays V for storing volumes and C for storing values
    # (...and fill the arrays with zero values)
    V <- rep(0, n)
    # SET V to 1-dimensional double array of size n
    C <- rep(0, n)
    # SET C to 1-dimensional double array of size n

    # Initialize arrays A for storing timber assortment indices and L for
    # storing log bottom positions (...and fill the arrays with zero values)
    A <- rep(0, n)
    # SET A to 1-dimensional integer array of size n
    L <- rep(0, n)
    # SET L to 1-dimensional integer array of size n

    # Initialize some auxiliary variables
    # SET t to 1
    t <- 1
    # SET d_top to 0.0
    d_top <- 0.0
    # SET d_min to 0.0
    d_min <- 0.0
    # SET v to 0.0
    v <- 0.0
    # SET c to 0.0
    c <- 0.0
    # SET v_tot to 0.0
    v_tot <- 0.0
    # SET c_tot to 0.0
    c_tot <- 0.0

    for (i in 1:n) {
        for (j in 1:m) {
            # Get a location indice t for the top segment of the current stem
            # piece when the location indice for the bottom segment is i
            # (divide the height with the stem divisor)
            t <- i + P[j, 3] / div
            if (t < n) {
                # Get the top diameter of the current tree segment and check
                # if the diameter is greater than the minimum assortment
                # diameter defined in the price matrix P
                d_top <- T[t, 1]
                d_min <- P[j, 2]
                if (d_top >= d_min) {
                    # Calculate current tree stem's (bottom at i, top at t)
                    # volume v and the cumulative value c
                    v <- T[t, 3] - T[i, 3]
                    c <- v * P[j, 4]
                    # Calculate the total volume and value at location i
                    v_tot <- v + V[i]
                    c_tot <- c + C[i]
                    # If total value, calculated as the value of the current
                    # log plus all the logs below i, is higher than the
                    # existing value in t, overwrite the existing value
                    # with c_tot
                    if (c_tot > C[t]) {
                        V[t] <- v_tot
                        C[t] <- c_tot
                        A[t] <- P[j, 1]
                        L[t] <- i
                    } # if
                } # if
            } # if
        } # for j
    } # for i

    # Get the location indice for the maximum value in C[t] array by calling
    # appropriate function
    # CALL get_max_indice with C RETURNING maxi
    maxi <- which.max(C)

    # Define arrays for storing timber assortment volumes and values
    # SET VOLUMES to 1-dimensional double array with size equal to number of assortments
    nas <- unique(P[, 1])
    VOLUMES <- rep(0, length(nas))
    # SET VALUES to 1-dimensional double array with size equal to number of assortments
    VALUES <- rep(0, length(nas))

    # define some auxiliary variables
    a <- 1
    l <- 1

    # Cut the tree to optimal length logs and divide the values and
    # volumes to corresponding assortments, start from the top
    while (maxi > 0) {
        a <- A[maxi]
        l <- L[maxi]
        VOLUMES[a] <- VOLUMES[a] + V[maxi] - V[l]
        VALUES[a] <- VALUES[a] + C[maxi] - C[l]
        # Move to the next stem piece (under the current piece)
        maxi <- l
    } # while

    # OUTPUTS:
    #        VOLUMES -- volumes of each timber assortment
    #        VALUES -- values of each timber assortment
    list(volumes = VOLUMES, values = VALUES)
}
