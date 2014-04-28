/*	$Id: expand.c,v 1.9 2014/04/28 02:15:09 cheungr Exp $	*/

/* CS 352 -- expand.c, part of the MiniShell!
 *
 *
 *    April 26, 2014, Roy Cheung
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include "proto.h"

/*This is a helper function that given strings and the change, change it*/
int replacer(char* dst, char* env, int curr_count, int newsize, int *incrementer){
	int varcounter = 0;
	/* Checks to make sure getenv or whatever, actually returned something */
	if (env != NULL){
		while(*env != '\0'){
			curr_count++;
			if(curr_count > newsize){
				dprintf(2, "%s", "msh: expansion too long \n");
				goto fail;
			}
			*dst = *env;
			dst++;
			env++;
			varcounter++;
		}
	}	
	/* This is replace ${} with ""
		Nelson msh doesn't do that, so... commented out.
	else{
		curr_count+=2;
		if(curr_count > newsize){
			dprintf(2, "%s", "msh: expansion too long \n");
			goto fail;
		}
		*dst='\"';
		dst++;
		*dst='\"';
		dst++;
		varcounter+=2;
	} */
	*incrementer = varcounter;
	return 0;
	
fail:
	return -1;
}

/* Main expander */
int expand(char *orig, char *new, int newsize){
	char* src = &orig[0];
	char* dst = &new[0];
	char* path;
	
	int count = 0;
	int varsize = 0;
	
	/* Loops through src */
	while (*src){
		if(*src == '$'){
			src++;
			if(*src == '{'){
				src++;
				int pathc = 0;
				path = src;
				while(*path != '}'){
					path++;
					pathc++;
					if(*path == '\0'){
						dprintf(2, "%s", "msh: no matching } \n");
						goto fail;
					}
				}
				/* Make the env_var char array */
				char env_var[pathc];
				int i = 0;
				while(*src != '}'){
					env_var[i] = *src;
					i++;
					src++;
				}
				if(*src == '}'){
					src++;
				}
				
				/* Sets null terminating */
				env_var[i] = '\0';
				
				/* Gets from environment varables */
				char *pENV = getenv(env_var);
				if (replacer(dst, pENV, count, newsize, &varsize) == 0){					
					count+=varsize;
					dst+=varsize;
				}
				else{
					goto fail;
				}
			}
			/* if they do $$ */
			else if(*src == '$'){
				/* build pid string */
				int pid = getpid();
				char buffer[10]; /* ~ max for x64 pid */
				snprintf(buffer, 10,"%d", pid);
				char *pENV = (buffer);
				/* send it to replacer */
				if (replacer(dst, pENV, count, newsize, &varsize) == 0){					
					count+=varsize;
					dst+=varsize;
				}
				else{
					goto fail;
				}
				src++;
			}
			else{
				count++;
				if(count > newsize){
					dprintf(2, "%s", "msh: expansion too long \n");
					goto fail;
				}
				src--;
				*dst = *src;
				dst++;
				src++;
			}
		}
		else{
			count++;
			if(count > newsize){
				dprintf(2, "%s", "msh: expansion too long \n");
				goto fail;
			}
			*dst = *src;
			dst++;
			src++;
		}
	}
	
	*dst = '\0';

	return 0;
fail:
	return -1;	

}
