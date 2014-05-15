/*	$Id: msh.c,v 1.15 2014/05/09 04:24:45 cheungr Exp $	*/

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
#include <sys/wait.h>
#include "global.h"
#include "proto.h"

/* Constants */

#define LINELEN 1024

/* Prototypes */

void processline (char *line);

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
    

    while (1) {

          /* prompt and get line */
  		if(inter == 1){
  			fprintf (stderr, "%% ");
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
  		processline (buffer);

    }

    if (!feof(stdin))
        perror ("read");

    return 0;		/* Also known as exit (0); */
}

/* processline function */

void processline (char *line)
{
    pid_t  cpid;
    int    status;
    char   **argv;
	  char   newline[LINELEN];
	
	/* calls expand to do the expand thing */
	if (expand(line, newline, LINELEN) != 0){
	  return;
	}
	
	/* call arg_parse, and get argc from it */
    int argc = arg_parse(newline, &argv);
    
    if (argc == 0){
      return;
    }    
	   
    /* tries to do_builtin in the args */
    /* biexit is the global exit status value */
    biexit = do_builtin(argc, argv);
    if(biexit != -1){
      free(argv);
      return;
    }

    /* Start a new process to do the job. */
    cpid = fork();
    if (cpid < 0) {
      perror ("fork");
      free(argv);
      return;
    }

    /* Check for who we are! */
    if (cpid == 0) {
      /* We are the child! */
      execvp (argv[0], argv);
      perror ("exec");
      free(argv);
      exit (127);
    }

    /* Have the parent wait for child to complete */
    if (wait (&status) < 0)
      perror ("wait");
    if (WIFEXITED(status)){
      biexit = WEXITSTATUS(status);
    }
    else{
      biexit = 127;
    }

}
