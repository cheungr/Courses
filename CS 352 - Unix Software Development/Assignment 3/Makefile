#	$Id: Makefile,v 1.3 2014/04/27 21:51:45 cheungr Exp $

# CS 352 -- Makefile
# Created April 25, 2014 Roy Cheung

 
#Makefile.
CC=gcc

#Compile flags:
CFLAGS=-g -Wall

#Sources and Objects. Sources is all .c files within the dir
	#SOURCES=$(wildcard *.c) <TIL This is bad implementation
SOURCES=msh.c builtin.c arg_parse.c expand.c
OBJS=$(SOURCES:.c=.o)

msh: $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o msh
	
#Dependency
$(OBJS): proto.h

#Clean
clean: 
	rm -rf msh *o *~

