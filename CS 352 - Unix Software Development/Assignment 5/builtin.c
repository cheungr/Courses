/*	$Id: builtin.c,v 1.21 2014/05/27 04:37:20 cheungr Exp $	*/

/* CS 352 -- Builtin.c, part of the MiniShell!
 *
 *   Sept 21, 2000,  Phil Nelson
 *   Modified April 8, 2001
 *   Modified January 6, 2003
 *   Modified April 13, 2014 Roy Cheung
 */
#include <stdio.h>
#include <string.h>
#include <bsd/string.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/stat.h>
#include <pwd.h>
#include <grp.h>
#include <time.h>
#include "global.h"
#include "proto.h"


/* This is the exit built in function */
int bi_exit(int argc, char **argvp, int outfd){
	if (argc == 1){
		exit(0);
	}
	else{
		exit(atoi(argvp[1]));
	}
}

/* This is the aecho built in function */
int aecho(int argc, char **argvp, int outfd){
	
	/* If only one argument, print out a new line */
	if(argc ==1){
		dprintf(1, "%c", '\n');
		return 1;
	}

	int i = 1;;
	int newlineyo = -1;
	int buffer_size = globalsize;

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
	dprintf(outfd, "%s", string);

/* snprintf string building derived from example from cplusplus.com
            snprintf example. 	http://i.cheungr.com/snprintf */
    return 0;
}

/* This is the setenv built in function */
int bi_setenv(int argc, char **argvp, int outfd){
	if(argc != 3){
		dprintf(outfd, "usage: envset name value%c", '\n');
		return 1;
	}
	
	if(setenv(argvp[1], argvp[2], 1) != 0){
		dprintf(outfd, "usage: envset name value%c", '\n');
		return 1;
	}
	return 0;
}

/* This is the unsetenv built in function */
int bi_unsetenv(int argc, char **argvp, int outfd){
	if(argc != 2){
		dprintf(outfd, "usage: envunset name%c", '\n');
		return 1;
	}
	
	if(unsetenv(argvp[1]) != 0){
		dprintf(outfd, "usage: envunset name%c", '\n');
		return 1;
	}
	
	return 0;
}

/* This is the cd built in function */
int bi_cd(int argc, char **argvp, int outfd){
	if (argc == 1){
		if(chdir(getenv("HOME")) != 0){
			dprintf(2, "cd: %s \n", strerror(errno));
			return 1;
		}
		return 0;
	}
	else if(argc == 2){
		if (chdir(argvp[1]) != 0){
			dprintf(2, "cd: %s: %s \n", argvp[1], strerror(errno));
			return 1;
		}
		return 0;
	}	
	else{
		dprintf(outfd, "usage: cd [dir]%c", '\n');
		return 1;
	}
	return 0;
}

/* This is the shift built in function */
int bi_shift(int argc, char **argvp, int outfd){
	int i = 0;
	int shifting = 1;
	if(argc > 2){
		dprintf(outfd, "usage shift [n]%c", '\n');
		return 1;
	}
	else if(argc > 1){
		while (argvp[1][i] != 0){
			if(isdigit(argvp[1][i]) == 0){
				dprintf(outfd, "usage shift [n]%c", '\n');
				return 1;
			}
			i++;
		}
		shifting = atoi(argvp[1]);
		if(shifting >=  (mainargn - shift - 1)){
			dprintf(2, "shift: not enough parameters for shift of %d \n", shifting);
			return 1;
		}
		else{
			shift += shifting;
			return 0;
		}
	}
	else{
		if(shifting >=  (mainargn - shift - 1)){
			dprintf(2, "shift: not enough parameters for shift of %d \n", shifting);
			return 1;
		}
		shift = shifting;
		return 0;
	}
}

/* This is the unshift built in function */
int bi_unshift(int argc, char **argvp, int outfd){
	int i = 0;
	int shifting = 0;
	if(argc > 2){
		dprintf(outfd, "usage unshift [n]%c", '\n');
		return 1;
	}
	else if(argc > 1){
		while (argvp[1][i] != 0){
			if(isdigit(argvp[1][i]) == 0){
				dprintf(outfd, "usage unshift [n]%c", '\n');
				return 1;
			}
			i++;
		}
		shifting = atoi(argvp[1]);
		if(shifting >  shift){
			dprintf(2, "unshift: not enough parameters for shift of %d \n", shifting);
			return 1;
		}
		else{
			shift -= shifting;
			return 0;
		}
	}
	else{
		if(shifting >  shift){
			dprintf(2, "shift: not enough parameters for shift of %d \n", shifting);
			return 1;
		}
		shift = 0;
		return 0;
	}
}

/* This is the sstat built in function */
int bi_sstat(int argc, char **argvp, int outfd){
	struct stat fileStats;
	struct passwd *user;
	struct group *group;
	/* permissions --- thing has 10 characters + 1 for null */
	char permissions[11];
	
	int currfile = 1;

	if(argc > 1){
		while(argc > currfile){
			if(stat(argvp[currfile], &fileStats)){
				dprintf(2, "%s: No such file or directory\n", argvp[currfile]);
				if (argc == 2){
					return 1;
				}
			}
			else{
				dprintf(outfd, "%s ", argvp[currfile]);
				user = getpwuid(fileStats.st_uid);
				group = getgrgid(fileStats.st_gid);
				strmode(fileStats.st_mode, permissions);

				if(user != NULL){
					dprintf(outfd, "%s ", user->pw_name);
				}
				else{
					dprintf(outfd, "%d ", fileStats.st_uid);
				}

				if(group != NULL){
					dprintf(outfd, "%s ", group->gr_name);
				}
				else{
					dprintf(outfd, "%d ", fileStats.st_gid);
				}

				dprintf(outfd, "%s", permissions);
				dprintf(outfd, "%zd ", fileStats.st_nlink);
				dprintf(outfd, "%zd ", fileStats.st_size);
				dprintf(outfd, "%s", ctime(&fileStats.st_mtime));
			}
			currfile++;
		}
	}
	else{
		dprintf(2, "stat: no files to stat %c", '\n');
		return 1;
	}

	return 0;
}

/* reads in a line of input from standard into envvariab */
int bi_read(int argc, char **argvp, int outfd){
	char buffer[1024]; //This is cause env system limit
	int end;
	if(argc != 2){
		dprintf(outfd, "usage read variable-name%c", '\n');
		return 1;
	}
	else{
		argvp++;
		//get the input from stdin
		if(fgets(buffer, 1024, stdin) != buffer){
			perror("input error");
		}
		end = strlen(buffer);
		if(buffer[end-1] == '\n'){
			buffer[end-1] = '\0';
		}
		//set env
		setenv(*argvp, buffer, 1);
	}
	return 0;
}
/* struct with the command and the command */
static struct{
	char *cmd;
	int (*callfunk) (int, char **, int outfd);
}
funs[] = {
	       {"exit", &bi_exit},
	       {"aecho", &aecho},
	       {"envset", &bi_setenv},
	       {"envunset", &bi_unsetenv},
	       {"cd", &bi_cd},
	       {"shift", &bi_shift},
	       {"unshift", &bi_unshift},
	       {"sstat", &bi_sstat},
	       {"read", &bi_read}
	   };

/* Update to number of functions in the funs list */
int funcount = 9;

/* Cause apparently for loop inital declarations are not allowed. */
int i;

/* Do_builtin function, takes in arg count and argvp. */
int do_builtin (int argc, char **argvp, int outfd){
	char *search = argvp[0];
    
    /* for all the functions, in the list, check and then call it. */
	for(i=0; i < funcount; i++){
		if(strcmp(search, funs[i].cmd) == 0){
			return funs[i].callfunk(argc, argvp, outfd);
		}
	}
    return -1;
}
