#!/usr/bin/make -f

PACKAGES= python3-embed

NUMCPUS=$(shell grep -c '^processor' /proc/cpuinfo)

TRGT=

CC   = $(TRGT)gcc
CXX  = $(TRGT)g++
AS   = $(TRGT)gcc -x assembler-with-cpp

LD   = $(TRGT)g++
AR   = $(TRGT)ar rvc

RM= rm --force --verbose

PYTHON= python3
CYTHON= cython3

PKGCONFIG= pkg-config

ifndef PACKAGES
PKG_CONFIG_CFLAGS=
PKG_CONFIG_LDFLAGS=
PKG_CONFIG_LIBS=
else
PKG_CONFIG_CFLAGS=`pkg-config --cflags $(PACKAGES)`
PKG_CONFIG_LDFLAGS=`pkg-config --libs-only-L $(PACKAGES)`
PKG_CONFIG_LIBS=`pkg-config --libs-only-l $(PACKAGES)`
endif

CFLAGS= \
	-Wall \
	-fwrapv \
	-fstack-protector-strong \
	-Wall \
	-Wformat \
	-Werror=format-security \
	-Wdate-time \
	-D_FORTIFY_SOURCE=2 \
	-fPIC

LDFLAGS= \
	-Wl,-O1 \
	-Wl,-Bsymbolic-functions \
	-Wl,-z,relro \
	-Wl,--as-needed \
	-Wl,--no-undefined \
	-Wl,--no-allow-shlib-undefined \
	-Wl,-Bsymbolic-functions \
	-Wl,--dynamic-list-cpp-new \
	-Wl,--dynamic-list-cpp-typeinfo

CYFLAGS= \
	-3 \
	--cplus \
	-X language_level=3 \
	-X boundscheck=False

CSTD=-std=gnu17
CPPSTD=-std=gnu++17

OPTS= -O2 -g

DEFS= \
	-DNDEBUG \
	-D_LARGEFILE64_SOURCE \
	-D_FILE_OFFSET_BITS=64

INCS= \
	-Iinclude

CYINCS= \
	-Icython

LIBS=

OBJS= \
	src/LayerGroup.o \
	src/Object.o \
	src/ImageLayer.o \
	src/ObjectGroup.o \
	src/ObjectTypes.o \
	src/Property.o \
	src/Tileset.o \
	src/Map.o \
	src/FreeFuncs.o \
	src/TileLayer.o \
	src/miniz.o \
	src/detail/pugixml.o

PYX_NAMES= gonlet shaders tmxlite

PYX_SRCS= $(PYX_NAMES:%=src/%.pyx)
PYX_CPPS= $(subst .pyx,.cpp,$(PYX_SRCS))
PYX_OBJS= $(subst .pyx,.o,$(PYX_SRCS))

all: ../tmxlite.so

../tmxlite.so: ./tmxlite.o $(OBJS)

%.bin:
	$(LD) $(CPPSTD) $(CSTD) $(LDFLAGS) $(PKG_CONFIG_LDFLAGS) -o $@ $+ $(LIBS) $(PKG_CONFIG_LIBS)

%.so:
	$(LD) -shared $(CPPSTD) $(CSTD) $(LDFLAGS) $(PKG_CONFIG_LDFLAGS) -o $@ $+ $(LIBS) $(PKG_CONFIG_LIBS)

%.a:
	$(AR) $@ $+

%.o: %.cpp
	$(CXX) $(CPPSTD) $(OPTS) -o $@ -c $< $(DEFS) $(INCS) $(CFLAGS) $(PKG_CONFIG_CFLAGS)

%.o: %.c
	$(CC) $(CSTD) $(OPTS) -o $@ -c $< $(DEFS) $(INCS) $(CFLAGS) $(PKG_CONFIG_CFLAGS)

%.cpp: %.pyx
	$(CYTHON) $(CYFLAGS) $(CYINCS) -o $@ $<


clean:
	$(RM) $(OBJS) $(PYX_OBJS)
	$(RM) $(subst .pyx,.cpp,$(PYX_SRCS))
	$(RM) $(subst .pyx,_api.cpp,$(PYX_SRCS))
	$(RM) $(subst .pyx,.h,$(PYX_SRCS))
	$(RM) $(subst .pyx,_api.h,$(PYX_SRCS))
	@find . -name '*.o' -exec $(RM) {} +
	@find . -name '*.a' -exec $(RM) {} +
	@find . -name '*.so' -exec $(RM) {} +
	@find . -name '*.pyc' -exec $(RM) {} +
	@find . -name '*.pyo' -exec $(RM) {} +
	@find . -name '*.bak' -exec $(RM) {} +
	@find . -name '*~' -exec $(RM) {} +
	@$(RM) core

.PHONY: all clean
