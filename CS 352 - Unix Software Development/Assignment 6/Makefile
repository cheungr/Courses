#	$Id: Makefile,v 1.6 2014/06/06 16:56:38 cheungr Exp $

# CS 352 -- Makefile
# Created April 25, 2014 Roy Cheung

 
#Makefile.
CC=gcc

#Compile flags:
CFLAGS=-g -Wall

#Sources and Objects. Sources is all .c files within the dir
	#SOURCES=$(wildcard *.c) <TIL This is bad implementation
SOURCES=msh.c builtin.c arg_parse.c expand.c scriptin.c
OBJS=$(SOURCES:.c=.o)

msh: $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -lbsd -o msh
	
#Dependency
$(OBJS): proto.h global.h

#Clean
clean: 
	rm -rf msh *o *~

