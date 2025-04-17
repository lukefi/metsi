/************************************************************************

Program:	ykjtm35

Module:		ykjtm35.c

Description:	This module contains a program to transform ykj
		coordinates to ETRS-TM35FIN coordinates.
		Fortran bindings are compiled if F_BINDINGS is set.

		The bindings use the same names (from Fortran) as
		the original functions but all parameters are
		value parameters.

Usage:

Programmer:	Kai Makisara

Revision:	

Last modified: Wed Dec  2 10:32:10 2009 by makisara@tukki.metla.fi

*************************************************************************

	Copyright by FINNISH FOREST RESEARCH INSTITUTE
	Address: PO Box 18 (Jokiniemenkuja 1), FIN-01301 Vantaa, Finland
	Phone:   +358-10-2111
	Telefax: +358-10-211 2202
	Email:	 Kai.Makisara@metla.fi (Internet)

************************************************************************/
/* $Log: ykjtm35.c,v $
/* Revision 1.1  2010/02/05 11:01:07  redsven
/* MELA200-versio tallennettu 5.2.2010
/*
 * Revision 1.0  2010-02-03 13:36:05+02  redsven
 * Initial revision
 *
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "triangles.h"
#include "points.h"

#define F_BINDINGS 1

static int current_triangle = -1;

#define MAXTRIANGLE 167000.0

static int *point_map;

static void get_triangle(int, double *, double *, int);

/* Creates a mapping from the point indices to point array */
static void map_points(void)
{
    int i, n;

    if (point_map)
	return;

    for (i=n=0; i < nbr_refpoints; i++)
	if (refpoints[i].index > n)
	    n = refpoints[i].index;

    if ((point_map = malloc((n + 1) * sizeof(int))) == NULL) {
	fprintf(stderr, "Can't allocate point map. Aborting.\n");
	exit(1);
    }
    for (i=0; i <= n; i++)
	point_map[i] = -1;

    for (i=0; i < nbr_refpoints; i++)
	point_map[refpoints[i].index] = i;

#ifdef TESTI
    {
	int j, ykj;
	double maxx, maxy, maxd, d, dd;
	double ptsx[3], ptsy[3];

	for (ykj=0; ykj < 2; ykj++) {
	    for (i=0, maxx=maxy=maxd=0.0; i < nbr_triangles; i++) {
		get_triangle(i, ptsx, ptsy, ykj);
		for (j=0; j < 3; j++) {
		    d = fabs(ptsx[(j + 1) % 3] - ptsx[j]);
		    if (d > maxx)
			maxx = d;
		    dd = d * d;
		    d = fabs(ptsy[(j + 1) % 3] - ptsy[j]);
		    if (d > maxy)
			maxy = d;
		    dd = sqrt(dd + d * d);
		    if (dd > maxd)
			maxd = dd;
		}
	    }
	    printf("ykj: %d maxx: %10.2lf maxy: %10.2lf maxd: %10.2lf\n",
		   ykj, maxx, maxy, maxd);
	}
    }

#endif

    return;
}


static void get_triangle(int ind, double *ptsx, double *ptsy, int ykj)
{
    int i, rpi;
    int coordoff = (ykj ? 0 : 2);
    for (i=0; i < 3; i++) {
	rpi = point_map[triangles[ind].index[i]];
	if (rpi < 0) {
	    fprintf(stderr, "Triangle refers to non-existing point. Aborting.\n");
	    exit(1);
	}
	ptsx[i] = refpoints[rpi].coords[coordoff];
	ptsy[i] = refpoints[rpi].coords[coordoff + 1];
    }
}


/* Use cross products to check that the point is on the same side of
   the line joining two points than the third point is. */
static int check_triangle(int ind, double x, double y, int ykj)
{
    int it1, it2, it3;
    double ptsx[3], ptsy[3], t1, t2, t3;

    map_points();
    get_triangle(ind, ptsx, ptsy, ykj);
    /* The triangle max dimension is MAXTRIANGLE m */
    t1 = ptsx[0] - x;
    t2 = ptsy[0] - y;
    if (t1 * t1 + t2 * t2 > MAXTRIANGLE * MAXTRIANGLE)
	return 0;

    t1 = (ptsx[1] - ptsx[0]) * (y - ptsy[0]) - (ptsy[1] - ptsy[0]) * (x - ptsx[0]);
    t2 = (ptsx[2] - ptsx[1]) * (y - ptsy[1]) - (ptsy[2] - ptsy[1]) * (x - ptsx[1]);
    t3 = (ptsx[0] - ptsx[2]) * (y - ptsy[2]) - (ptsy[0] - ptsy[2]) * (x - ptsx[2]);

    it1 = (t1 == 0) || ((t1 > 0) == ((ptsx[1] - ptsx[0]) * (ptsy[2] - ptsy[0]) -
				     (ptsy[1] - ptsy[0]) * (ptsx[2] - ptsx[0]) > 0));
    it2 = (t2 == 0) || ((t2 > 0) == ((ptsx[2] - ptsx[1]) * (ptsy[0] - ptsy[1]) -
				     (ptsy[2] - ptsy[1]) * (ptsx[0] - ptsx[1]) > 0));
    it3 = (t3 == 0) || ((t3 > 0) == ((ptsx[0] - ptsx[2]) * (ptsy[1] - ptsy[2]) -
				     (ptsy[0] - ptsy[2]) * (ptsx[1] - ptsx[2]) > 0));

    return it1 && it2 && it3;
}


static int find_triangle(double x, double y, int ykj)
{
    int i;

    if (current_triangle >= 0) {
	if (check_triangle(current_triangle, x, y, ykj))
	    return current_triangle;
    }


    for (i=0; i < nbr_triangles; i++)
	if (check_triangle(i, x, y, ykj))
	    break;
    if (i < nbr_triangles)
	current_triangle = i;
    else
	current_triangle = -1;

    return current_triangle;
}


int ykjtm35fin(double x, double y, double *u, double *v, int ykjtotm35)
{
    int i, tri;
    double ptsx[3], ptsy[3], ptsu[3], ptsv[3];
    double c0x, c0y, c1x, c1y, c2x, c2y;
    double w[3];
    tri = find_triangle(x, y, ykjtotm35);
    if (tri < 0)
	return 0;

    get_triangle(tri, ptsx, ptsy, ykjtotm35);
    get_triangle(tri, ptsu, ptsv, !ykjtotm35);

    c0x = ptsy[2] - ptsy[1];
    c0y = ptsx[1] - ptsx[2];
    c1x = ptsy[2] - ptsy[0];
    c1y = ptsx[0] - ptsx[2];
    c2x = ptsy[1] - ptsy[0];
    c2y = ptsx[0] - ptsx[1];

    w[0] = ((x - ptsx[1]) * c0x + (y - ptsy[1]) * c0y) /
	((ptsx[0] - ptsx[1]) * c0x + (ptsy[0] - ptsy[1]) * c0y);
    w[1] = ((x - ptsx[0]) * c1x + (y - ptsy[0]) * c1y) /
	((ptsx[1] - ptsx[0]) * c1x + (ptsy[1] - ptsy[0]) * c1y);
    w[2] = ((x - ptsx[0]) * c2x + (y - ptsy[0]) * c2y) /
	((ptsx[2] - ptsx[0]) * c2x + (ptsy[2] - ptsy[0]) * c2y);

    *u = *v = 0.0;
    for (i=0; i < 3; i++) {
	*u += w[i] * ptsu[i];
	*v += w[i] * ptsv[i];
    }


    return 1;
}


int ykj_to_tm35fin(double x, double y, double *u, double *v)
{
    return ykjtm35fin(x, y, u, v, 1);
}


int tm35fin_to_ykj(double u, double v, double *x, double *y)
{
    return ykjtm35fin(u, v, x, y, 0);
}


#ifdef TEST
int main(int argc, char **argv)
{
    int i, ykjtotm35, quiet = 0;
    char *from, *to, *name;
    double x, y, u, v;

    i = strlen("ykjtm35");
    name = argv[0] + strlen(argv[0]) - i;

    for (i=1; i < argc; i++)
	if (*argv[i] == '-')
	    switch (*(argv[i] + 1)) {
	    case 'q':
		quiet = 1;
		break;
	    default:
		fprintf(stderr, "Usage: %s [-q]\n", name);
		return *(argv[i] + 1) != 'h';
	    }

    ykjtotm35 = !strcmp(name, "ykjtm35");

    if (ykjtotm35) {
	from = "Ykj";
	to = "TM35FIN";
    }
    else {
	from = "TM35FIN";
	to = "Ykj";
    }

    for ( ; ; ) {
	if (!quiet)
	    printf("%s x, y: ", from);
	x = y = 0.0;
	scanf("%lf%*[, ]%lf", &x, &y);
	if (x == 0.0 && y == 0.0)
	    break;
	if (ykjtotm35)
	    i = ykj_to_tm35fin(x, y, &u, &v);
	else
	    i = tm35fin_to_ykj(x, y, &u, &v);
	if (i) {
	    if (quiet) {
		printf("%f %f %f %f\n", x, y, u, v);
		continue;
	    }
	    printf("%s: %f %f\n", to, u, v);
#if 0
	    if (!ykjtotm35)
		i = ykj_to_tm35fin(u, v, &x, &y);
	    else
		i = tm35fin_to_ykj(u, v, &x, &y);
	    if (i) {
		printf("%s: %f %f\n\n", from, x, y);
	    }
	    else
		printf("Conversion back failed.\n\n");
#endif
	}
	else
	    printf("Conversion failed.\n");
    }

    return 0;
}
#endif


#if F_BINDINGS

/* The Fortran bindings for the functions */

/* Define the names as the Fortran implementation requires */
#define F_YKJTM35FIN ykjtm35fin_
#define F_YKJ_TO_TM35FIN ykj_to_tm35fin_
#define F_TM35FIN_TO_YKJ tm35fin_to_ykj_


int F_YKJTM35FIN(double *x, double *y, double *u, double *v, int *ykjtotm35)
{
    return ykjtm35fin(*x, *y, u, v, *ykjtotm35);
}


int F_YKJ_TO_TM35FIN(double *x, double *y, double *u, double *v)
{
    return ykj_to_tm35fin(*x, *y, u, v);
}


int F_TM35FIN_TO_YKJ(double *u, double *v, double *x, double *y)
{
    return tm35fin_to_ykj(*u, *v, x, y);
}

#endif
