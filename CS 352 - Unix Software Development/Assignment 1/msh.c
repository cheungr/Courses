/* CS 352 -- Mini Shell!  
 *
 *   Sept 21, 2000,  Phil Nelson
 *   Modified April 8, 2001 
 *   Modified January 6, 2003
 *	 Modified April 4, 2014 Roy Cheung
 */

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>


/* Constants */ 

#define LINELEN 1024

/* Prototypes */

void processline (char *line);
char ** arg_parse (char *line);

/* Shell main */

int
main (void)
{
    char   buffer [LINELEN];
    int    len;

    while (1) {

        /* prompt and get line */
	fprintf (stderr, "%% ");
	if (fgets (buffer, LINELEN, stdin) != buffer)
	  break;

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


char ** arg_parse (char *line)
{
	
	int argc = 0,
		i = 0,
		len = strlen(line),
		k = 0;
	char **argv;
	
	/* count number of arguments */
	while(i < len){
		if(line[i] != ' '){
			argc++;
			while(line[i] != ' '){
				i++;
				if (i > len){
					break;
				}
			}
		}
		else{
			i++;
		}
	}
	
	/* allocate memory for array of arguments */
	argv = (char **)malloc(argc * sizeof(char *) + 1);
	if (!argv)
		perror("malloc");
	
	/* Assigns pointers and sets space to 0 at end of argument */
	i = 0;
	while(i < len){
		if(line[i] != ' '){
			if (k < argc){
				argv[k] = &line[i];
				k++;
			}
			i++;
			while(line[i] != ' '){
				i++;
				if (i > len){
					break;
				}
			}
			line[i] = 0;
			i++;
		}
		else{
			i++;
		}
	}
	/* Sets NULL pointer */
	argv[argc] = NULL;
	
	return argv;
}


void processline (char *line)
{
    pid_t  cpid;
    int    status;
    
    char **argv = arg_parse(line);    
    
    /* Start a new process to do the job. */
    cpid = fork();
    if (cpid < 0) {
      perror ("fork");
      return;
    }
    
    /* Check for who we are! */
    if (cpid == 0) {
      /* We are the child! */
      execvp (argv[0], argv);
      perror ("exec");
      exit (127);
    }
    
    /* free up args */    
    free(argv);
    
    /* Have the parent wait for child to complete */
    if (wait (&status) < 0)
      perror ("wait");
}


