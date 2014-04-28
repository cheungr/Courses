/*	$Id: builtin.c,v 1.4 2014/04/28 00:28:20 cheungr Exp $	*/

/* CS 352 -- Builtin.c, part of the MiniShell!
 *
 *   Sept 21, 2000,  Phil Nelson
 *   Modified April 8, 2001
 *   Modified January 6, 2003
 *   Modified April 13, 2014 Roy Cheung
 */
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>
#include "proto.h"

/* This is the exit built in function */
void bi_exit(int argc, char **argvp){
	if (argc == 1){
		exit(0);
	}
	else{
		exit(atoi(argvp[1]));
	}
}

/* This is the aecho built in function */
void aecho(int argc, char **argvp){
	
	/* If only one argument, print out a new line */
	if(argc ==1){
		dprintf(1, "%c", '\n');
		return;
	}

	int i = 1;;
	int newlineyo = -1;
	int buffer_size = 1024;

	/* check for -n in the argument */
	if(strcmp(argvp[i], "-n") == 0){
		newlineyo = 0;
		i++;
	}

	/* make the string with a buffer of 1024 */
	char string [buffer_size];

	/* bytes written holder */	
	int collect = snprintf(string, buffer_size, "%s", argvp[i]);
	i++;

	/* loop through all the arguments and write to the buffer string */
	for(;i < argc; i++){
		collect += snprintf(string + collect, 
							buffer_size - collect, 
							" %s", argvp[i]);
	}

	/* if -n, then -1. so add newline to the string buffer */	
	if(newlineyo == -1){
		snprintf(string + collect, buffer_size - collect, "\n");
	}
	
	/* dprintf the string */
	dprintf(1, "%s", string);

/* snprintf string building derived from example from cplusplus.com
            snprintf example. 	http://i.cheungr.com/snprintf */
}

/* This is the setenv built in function */
void bi_setenv(int argc, char **argvp){
	if(argc != 3){
		dprintf(1, "usage: envset name value%c", '\n');
		return;
	}
	
	if(setenv(argvp[1], argvp[2], 0) != 0){
		dprintf(1, "usage: envset name value%c", '\n');
		return;
	}

}

/* This is the unsetenv built in function */
void bi_unsetenv(int argc, char **argvp){
	if(argc != 2){
		dprintf(1, "usage: envunset name%c", '\n');
		return;
	}
	
	if(unsetenv(argvp[1]) != 0){
		dprintf(1, "usage: envunset name%c", '\n');
		return;
	}

}

/* This is the cd built in function */
void bi_cd(int argc, char **argvp){
	if (argc == 1){
		if(chdir(getenv("HOME")) != 0){
			dprintf(2, "cd: %s \n", strerror(errno));
		}
	}
	else if(argc == 2){
		if (chdir(argvp[1]) != 0){
			dprintf(2, "cd: %s: %s \n", argvp[1], strerror(errno));
		}
	}	
	else{
		dprintf(1, "usage: cd [dir]%c", '\n');
		return;
	}


}

/* struct with the command and the command */
static struct{
	char *cmd;
	void (*callfunk) (int, char **);
}
funs[] = {
	       {"exit", &bi_exit},
	       {"aecho", &aecho},
	       {"envset", &bi_setenv},
	       {"envunset", &bi_unsetenv},
	       {"cd", &bi_cd}
	   };

/* Update to number of functions in the funs list */
int funcount = 5;

/* Cause apparently for loop inital declarations are not allowed. */
int i;

/* Do_builtin function, takes in arg count and argvp. */
int do_builtin (int argc, char **argvp){
	char *search = argvp[0];
    
    /* for all the functions, in the list, check and then call it. */
	for(i=0; i < funcount; i++){
		if(strcmp(search, funs[i].cmd) == 0){
			funs[i].callfunk(argc, argvp);
			return 0;
		}
	}
    return -1;
}
