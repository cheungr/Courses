/*	$Id: msh.c,v 1.23 2014/05/27 06:57:33 cheungr Exp $	*/

/* CS 352 -- Mini Shell!
 *
 *   Sept 21, 2000,  Phil Nelson
 *   Modified April 8, 2001
 *   Modified January 6, 2003
 *	 Modified April 13, 2014 Roy Cheung
 */

#define MAINSHELL 

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/types.h>
#include <ctype.h>
#include <sys/wait.h>
#include "global.h"
#include "proto.h"

/* Constants */

#define LINELEN 200000

/* Prototypes */

int processline (char *line, int outfd, int waitflag);

/* Sig handler */
void sig_handler(int signo){
  if (signo == SIGINT){
    mysig = 0;
    // if(epid > 0){
    //   kill(epid,SIGINT);
    // }
  }
}

/* Shell main */

int main (int mainargc, char **mainargv)
{
	mainargn = mainargc;
	mainargl = mainargv;
    
    char   buffer [LINELEN];
    int    len;
    int    inter = 0;
    FILE * pFile;
    
    if(mainargc <= 1){
	    inter = 1;
	    pFile = stdin;
    }
    else{
    	pFile = fopen(mainargv[1], "r");
    	if (pFile == NULL){
    		dprintf(2, "./msh: Cannot open file %s \n", mainargv[1]);
    		exit(127);
    	}
    }
    
    if(signal(SIGINT, sig_handler) == SIG_ERR){
      perror("SIGINT error");
    }

    while (1) {
      mysig = 1;

		  char* EP1 = getenv("P1");
          /* prompt and get line */
  		if(inter == 1){
  			/* check to see if P1 in env is set or not */
  			if(EP1 != NULL){
  				dprintf(2, "%s", EP1);
  			}
  			else{
  				dprintf(2 , "%s", "% ");
  			}
  		}
  		if (fgets(buffer, LINELEN, pFile) == NULL){
  			if (inter != 1){
  				fclose(pFile);
  				exit(0);
  			}
        break;
  		}

  		    /* Get rid of \n at end of buffer. */
  		len = strlen(buffer);
  		if (buffer[len-1] == '\n')
  			buffer[len-1] = 0;


  		/* Run it ... */
  		(void) processline (buffer, 1, yeswait);

    }

    if (!feof(stdin))
        perror ("read");

    return 0;		/* Also known as exit (0); */
}

/* This removes comments from processing. Everything after # */
void nullifycomment(char *line){
  char* curr = &line[0];
  int quotesflag = 0;

  while(*curr){
    /* checks to see if it's in a quote */
    if(*curr == '"'){
      if(quotesflag == 1){
        quotesflag = 0;
      }
      else{
        quotesflag = 1;
      }
    }
    /* checks to see if it's a comment */
    if(*curr == '#'){
      curr--;
      if(isspace(*curr) != 0){
        curr++;
        if(quotesflag == 0){
          *curr = '\0';
          return;
        }
      }
      else{
        curr++;
      }
    }
    curr++;
  }

  return;
}

/* processline function */

int processline (char *line, int outfd, int waitflag)
{
  pid_t  cpid;
  int    status;
  char   **argv;
  char   newline[LINELEN];

  nullifycomment(line);

  /* calls expand to do the expand thing */
  if (expand(line, newline, LINELEN) != 0){
    return -1;
  }

  /* call arg_parse, and get argc from it */
  int argc = arg_parse(newline, &argv);

  if (argc == 0){
    return 0;
  }    
   
  /* tries to do_builtin in the args */
  /* biexit is the global exit status value */
  biexit = do_builtin(argc, argv, outfd);
  if(biexit != -1){
    free(argv);
    return 0;
  }

  /* Start a new process to do the job. */
  cpid = fork();
  if (cpid < 0) {
    perror ("fork");
    free(argv);
    return -1;
  }

  /* Check for who we are! */
  if (cpid == 0) {
    /* We are the child! */
    if(outfd != 1){
      if(dup2(outfd, 1) == -1){
        perror("dup2");
      }
    }
    execvp (argv[0], argv);
    perror ("exec");
    free(argv);
    exit (127);
  }

  if(outfd != 1){
    close(outfd);
  }

  /* Have the parent wait for child to complete */
  if(waitflag == yeswait){
    if (wait (&status) < 0)
      perror ("wait");
    if (WIFEXITED(status)){
      biexit = WEXITSTATUS(status);
    }
    else{
      biexit = 127;
    }
  }

  return cpid;
}
