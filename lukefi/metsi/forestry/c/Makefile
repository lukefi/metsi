# Variables

LIBDIR := lib
SOURCEDIR := source
SOURCES = $( addprefix $(SOURCEDIR)/, ykjtm35.c triangles.h points.h )


# Detect the operating system

ifeq ($(OS),Windows_NT)
    TARGET := $(LIBDIR)/ykjtm35.dll
    MKDIR := mkdir
    RM := rmdir /S /Q
else
    TARGET := $(LIBDIR)/ykjtm35.so
    OSFLAGS := -fPIC
    MKDIR := mkdir -p
    RM := rm -rf
endif

# Target

all: $(TARGET)

# Rules

$(LIBDIR) :
	$(MKDIR) $(LIBDIR)


$(LIBDIR)/ykjtm35.o : $(SOURCES) | $(LIBDIR)
	gcc -c $(SOURCEDIR)/ykjtm35.c -o $(LIBDIR)/ykjtm35.o $(OSFLAGS)


$(TARGET) : $(LIBDIR)/ykjtm35.o
	gcc -shared -o $(TARGET) $(LIBDIR)/ykjtm35.o


# Auxiliary

.PHONY : clean
clean :
	$(RM) $(LIBDIR)