# ----- Variables -----------------------------------------

LIBDIR := lib
SOURCEDIR := source
SOURCES = $( addprefix $(SOURCEDIR)/,ykjtm35.c triangles.h points.h )

# ----- Target --------------------------------------------

all: $(LIBDIR)/ykjtm35.dll


# ----- Rules ---------------------------------------------


$(LIBDIR) :
	mkdir $(LIBDIR)


$(LIBDIR)/ykjtm35.o : $(SOURCES) | $(LIBDIR)
	gcc -c $(SOURCEDIR)/ykjtm35.c -o $(LIBDIR)/ykjtm35.o


$(LIBDIR)/ykjtm35.dll : $(LIBDIR)/ykjtm35.o
	gcc -shared -o $(LIBDIR)/ykjtm35.dll $(LIBDIR)/ykjtm35.o


# ----- Auxiliary -----------------------------------------

.PHONY : clean
clean :
	rm  -rf $(LIBDIR)