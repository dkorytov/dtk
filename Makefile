GENIOD  = genericio
CC      = mpicxx
#datastar
<<<<<<< HEAD
GIOHEADERS =~/proj/hacc/trunk/genericio
GIO_FRONTEND_LIB = /home/dkorytov/proj/hacc/trunk/datastar.cpu/frontend/lib
GIO_MPI_LIB =/home/dkorytov/proj/hacc/trunk/datastar.cpu/mpi/lib
=======
GIOHEADERS =~/hacc/trunk/genericio
GIO_FRONTEND_LIB = /home/dkorytov/hacc/trunk/cooley/frontend/lib
GIO_MPI_LIB =/home/dkorytov/hacc/trunk/cooley/mpi/lib
>>>>>>> 0143810c3bd8a79d154db28b6fb7f75a1df6dd9a
#cooley
#GIOHEADERS =/gpfs/mira-home/dkorytov/hacc/trunk/genericio
#GIO_FRONTEND_LIB =/gpfs/mira-home/dkorytov/hacc/trunk/cooley/frontend/lib
CFLAGS  = -I. -g -I ${GIOHEADERS} -O3 
LDFLAGS = -L${GIO_MPI_LIB} -lGenericIOMPI -lfftw3f -lfftw3_threads -lfftw3 -lm -lpthreads
INC_DIR = dtk
SRC_DIR = src
OBJ_DIR = obj
LIB_DIR = lib
SOURCES = $(wildcard src/*.cpp)
OBJECTS = $(SOURCES:src/%.cpp=obj/%.o)
LIB_NAME= libdtk.a
LIB     = $(LIB_DIR)/${LIB_NAME}
PYLIB   = ${LIB_DIR}/libpygio.so
targets = ${LIB} 

<<<<<<< HEAD
all: ${PYLIB} ${LIB}
=======
all: ${PYLIB}
>>>>>>> 0143810c3bd8a79d154db28b6fb7f75a1df6dd9a

${PYLIB}: pygio/gio.hpp pygio/gio.cpp
	${CC} ${CFLAGS} -c -o  pygio/gio.o -fpic pygio/gio.cpp  -fopenmp
	${CC} -shared -o ${PYLIB} pygio/gio.o -L${GIO_FRONTEND_LIB} -Wl,--whole-archive,-export-dynamic -lGenericIO -Wl,--no-whole-archive -lgomp

<<<<<<< HEAD
${LIB}: ${OBJECTS}
	ar rcs ${LIB} ${OBJECTS}

${OBJECTS}: ${OBJ_DIR}/%.o : ${SRC_DIR}/%.cpp
	${CC} ${CFLAGS} -c -o $@ $<
=======
# ${LIB}: ${OBJECTS}
# 	ar rcs ${LIB} ${OBJECTS}

# ${OBJECTS}: ${OBJ_DIR}/%.o : ${SRC_DIR}/%.cpp
# 	${CC} ${CFLAGS} -c -o $@ $<
>>>>>>> 0143810c3bd8a79d154db28b6fb7f75a1df6dd9a


.PHONY:
clean:
	rm ${OBJECTS}
	rm ${LIB}
	rm ${PYLIB}

