/*	$Id: expand.c,v 1.23 2014/05/09 05:13:11 cheungr Exp $	*/

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
#include <ctype.h>
#include <dirent.h>
#include "global.h"
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
	
	char nstr[newsize];
	
	char* thisnum = &nstr[0];
	
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
			/* For $n, stuff */
		    else if (isdigit(*src)){
				*thisnum = *src;
				src++;
				thisnum++;
				while(isdigit(*src)){
					*thisnum = *src;
					thisnum++;
					src++;
				}
				thisnum = '\0';
				thisnum = &nstr[0];
				int argint = atoi(thisnum);
				argint++;
				/* add the shift */
				argint+=shift;
				if(mainargn == 1){
					argint--;
					argint-=shift;
				}
				/* if the number they want is larger than mainargn */
				/* return "" blank stuff. */
				if(argint > mainargn){
					*dst='\"';
					dst++;
					*dst='\"';
					dst++;	
				}
				else{
					/* build it to be returned to processline */
					char *pENV = mainargl[argint];
					if (replacer(dst, pENV, count, newsize, &varsize) == 0){					
						count+=varsize;
						dst+=varsize;
					}
					else{
						goto fail;
					}
				}			
			}
			/* Get the total count of arguments */
			else if(*src == '#'){
				int currnum = mainargn;
				if(mainargn > 1){
					currnum--;
				}
				/* Get add the shiftin */
				currnum-=shift;
				char buffer[newsize];
				snprintf(buffer, newsize, "%d", currnum);
				char *pENV = buffer;
				if (replacer(dst, pENV, count, newsize, &varsize) == 0){					
						count+=varsize;
						dst+=varsize;
				}
				else{
					goto fail;
				}
				src++;
			}
			/* if they do $?, print out the last exit value */
			else if(*src == '?'){
				char buffer[newsize];
				snprintf(buffer, newsize, "%d", biexit);
				char *pENV = buffer;
				if(replacer(dst, pENV, count, newsize, &varsize) == 0){
					count+=varsize;
					dst+=varsize;
				}
				else{
					goto fail;
				}
				src++;
			}
			/* if they do $$ print out PID */
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
		/* for wildstar */
		else if(*src == '*'){
			src--;
			/* Check to see if there is whitespace before it or is in " */
			if (*src == ' ' || *src == '"'){
				src+=2;
				/* Check to see if it's lone * */
				if((*src == ' ') || (*src == 0)){
					src--;
					char buffer[newsize];
					struct dirent *pDirent;
					DIR *pDir;

					memset(buffer, '\0', sizeof(buffer));

					pDir = opendir(".");
					if(pDir == NULL){
						goto fail;
					}
					int i = 0;
					while((pDirent = readdir(pDir)) != NULL){
						if(pDirent->d_name[0] != '.'){
						 i+= snprintf(buffer+i, newsize, "%s ", pDirent->d_name);
						}
					}
					closedir(pDir);

					char *pENV = (buffer);
					if(replacer(dst, pENV, count, newsize, &varsize) == 0){
						count+=varsize;
						dst+=varsize;
					}
					else{
						goto fail;
					}
					src++;
				}
				else if(*src != '0'){
					/* build it */
					char suffix[255];
					char* sufptr = &suffix[0];
					char thisfName[255];
					int quote = 0;

					char buffer[newsize];
					struct dirent *pDirent;
					DIR *pDir;
					size_t namelen;
				
					memset(suffix, '\0', sizeof(suffix));
					memset(buffer, '\0', sizeof(buffer));
					memset(thisfName, '\0', sizeof(thisfName));

					/* For all the characters after wildcard add to char */
					while(*src != 0 && *src != ' ' && *src != '"'){
						*sufptr = *src;
						src++;
						sufptr++;
						if(*src == '"'){
							quote = 1;
						}
					
					}
					size_t suffixlen = strlen(suffix);
					pDir = opendir(".");
					if(pDir == NULL){
						goto fail;
					}
					int i = 0;
					/* For every single dir entry, compare and see, then build it. */
					while((pDirent = readdir(pDir)) != NULL){
						if(pDirent->d_name[0] != '.'){
						 	snprintf(thisfName, 255, "%s ", pDirent->d_name);
							namelen = strlen(thisfName) - 1;
							int addsize = namelen - suffixlen;
							if(strncmp(thisfName + addsize, suffix, suffixlen) == 0){
								i+=snprintf(buffer+i, 1024, "%s", thisfName);
							}
						}
					}
					closedir(pDir);

					if((int)strlen(buffer) != 0){
						char *pENV = (buffer);
						if(replacer(dst, pENV, count, newsize, &varsize) == 0){
							count+=varsize;
							dst+=varsize;
						}
						else{
							goto fail;
						}
						src++;
					}
					else{
						src--;
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

					/* Add the ending " if it was there in the first place */
					if(quote){
						dst--;
						*dst = '"';
						dst++;	
					}	
				}
				else{
					src--;
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
			else if(*src == '\\'){
				dst--;
				src++;
				count++;
				if(count > newsize){
					dprintf(2, "%s", "msh: expansion too long \n");
					goto fail;
				}
				*dst = *src;
				dst++;
				src++;
			}
			else{
				src++;
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
