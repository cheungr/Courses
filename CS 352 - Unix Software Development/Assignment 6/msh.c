/*	$Id: msh.c,v 1.28 2014/06/06 16:56:38 cheungr Exp $	*/

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
#include <fcntl.h>
#include "global.h"
#include "proto.h"

/* Constants */

#define LINELEN 200000

/* Prototypes */

int processline (char *line, int infd, int outfd, int waitflag, int expandflag);

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
		(void) processline (buffer, 0, 1, yeswait, yesexpand);

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

/* find pipeindex */

int pipefinder (char *line, int pipqflag){
  char *thisp = &line[0]; 
  int count = 0;
  while(*thisp){
    if(*thisp == '"'){
      if(pipqflag == 1){
        pipqflag = 0;
      }
      else{
        pipqflag = 1;
      }
    }
    if((*thisp == '|') && (pipqflag == 0)){
      *thisp = '\0';
      return count;
    }
    thisp++;
    count++;
  }
  return -1;
}


/* processline function */

int processline (char *line, int infd, int outfd, int waitflag, int expandflag)
{
  pid_t  cpid;
  int    status;
  char   **argv;
  char   newline[LINELEN];

  int cinfd = infd;
  int coutfd = outfd;
  int cerrfd = 2;

  nullifycomment(line);

  /* calls expand to do the expand thing */
  if(expandflag == yesexpand){
    if (expand(line, newline, LINELEN) != 0){
      return -1;
    }
  }
  else{
    strcpy(newline, line);
  }

  /* Pipeline identification */
  char *pip = &newline[0];
  int fds[2];
  int pipqflag = 0;

  int tinfd = infd;
  int pindex = 0;

  if((pindex = pipefinder(pip, pipqflag)) != -1){
    if(pipqflag == 0){
      while(pindex != -1){
        pipe(fds);
        pip[pindex] = '\0';
        cpid = processline(pip, tinfd, fds[1], nowait, noexpand);
        pip+= pindex;
        pip++;
        if(tinfd != infd){
          close(tinfd);
        }
        close(fds[1]);
        tinfd = fds[0];
        pindex = pipefinder(pip, pipqflag);
      }
      cpid = processline(pip, tinfd, outfd, waitflag, noexpand);
      close(tinfd);
      return cpid;
    }
  }



  /* Redirection string parsing and redirecting fds. */
  int quotesflag = 0;
  int quotesflag2 = 0;
  char *src = &newline[0];
  int stderrflag = 1;
  char namestr[1024];
  char *this = &namestr[0];

  /* Loops through all the data */
  while(*src){
    if(*src == '"'){
      if(quotesflag == 1){
        quotesflag = 0;
      }
      else{
        quotesflag = 1;
      }
    }
    if (*src == '<' && (quotesflag == 0)){
      *src = ' ';
      src++;
      while(*src == ' '){
        src++;
      }
      memset(namestr, '\0', 1024);
      this = &namestr[0];
      while(*src != ' ' && *src != '<' && *src != '>' && *src != '\0'){
        if(*src != '"'){
          *this = *src;
          this++;
          *src = ' ';
          src++;
        }
        else{
          *src = ' ';
          src++;
        }
      }
      if(strlen(namestr) == 0){
        dprintf(cerrfd, "%s: No file name for redirection operator\n", mainargl[0]);
        return -1;
      }
      if(cinfd != infd){
        close(cinfd);
      }
      cinfd = open(namestr, O_RDONLY, 0744);
      
      if(cinfd == -1){
        dprintf(cerrfd, "%s: %s: %s\n", mainargl[0], namestr, strerror(errno));
        return -1;
      }
    }
    else if(*src == '>' && (quotesflag == 0)){
      src--;
      if(*src == '2'){
        src--;
        if(*src == ' '){
          stderrflag = 0;
          src++;
          *src = ' ';
        }
        else{
          src++;
        }
      }
      src++;
      *src = ' ';
      src++;
      //It's a >>
      if (*src == '>'){
        *src = ' ';
        src++;
        while(*src == ' '){
          src++;
        }
        memset(namestr, '\0', 1024);
        this = &namestr[0];
        while(*src != ' ' && *src != '<' && *src != '>' && *src != '\0'){
          if(*src != '"'){
            *this = *src;
            this++;
            *src = ' ';
            src++;
          }
          else{
            *src = ' ';
            if(quotesflag2 == 1){
              quotesflag2 = 0;
            }
            else{
              quotesflag2 = 1;
            }
            src++;
          }
        } 
        if(quotesflag2 != 0){
          dprintf(cerrfd, "%s: unmatched quote(\")\n", mainargl[0]);
          return -1; 
        }
        if(strlen(namestr) == 0){
          dprintf(cerrfd, "%s: No file name for redirection operator\n", mainargl[0]);
          return -1;
        }
        //If it's 2>>
        if(stderrflag == 0){
          if(cerrfd != 2){
            close(cerrfd);
          }
          cerrfd = open(namestr, O_WRONLY | O_APPEND | O_CREAT, 0744);
        } 
        //Normal >>
        else{
          if(coutfd != outfd){
            close(coutfd);
          }
          coutfd = open(namestr, O_WRONLY | O_APPEND | O_CREAT, 0744);
        }
        if(coutfd == -1){
          dprintf(cerrfd, "%s: %s: %s\n", mainargl[0], namestr, strerror(errno));
          return -1;
        }
        stderrflag = 1;
      }
      //It's just a single >
      else{
        while(*src == ' '){
          src++;
        }
        this = &namestr[0];
        memset(namestr, '\0', 1024);
        while(*src != ' ' && *src != '<' && *src != '>' && *src != '\0'){
          if(*src != '"'){
            *this = *src;
            this++;
            *src = ' ';
            src++;
          }
          else{
            *src = ' ';
            if(quotesflag2 == 1){
              quotesflag2 = 0;
            }
            else{
              quotesflag2 = 1;
            }
            src++;
          }
        }
        //if it's 2>
        if(quotesflag2 != 0){
          dprintf(cerrfd, "%s: unmatched quote(\")\n", mainargl[0]);
          return -1; 
        }
        if(strlen(namestr) == 0){
          dprintf(cerrfd, "%s: No file name for redirection operator\n", mainargl[0]);
          return -1;
        }
        //Normal >
        if(stderrflag == 0){
          if(cerrfd != 2){
            close(cerrfd);
          }
          cerrfd =  open(namestr, O_WRONLY | O_CREAT | O_TRUNC, 0744);
        } 
        else{
          if(coutfd != outfd){
            close(coutfd);
          }
          coutfd = open(namestr, O_WRONLY | O_CREAT | O_TRUNC, 0744);
        }  
        if(coutfd == -1){
          dprintf(cerrfd, "%s: %s: %s\n", mainargl[0], namestr, strerror(errno));
          return -1;
        }
        stderrflag = 1;
      }
    }
    else{
      src++;
    }
  }
  
  /* call arg_parse, and get argc from it */
  int argc = arg_parse(newline, &argv);

  if (argc == 0){
    return 0;
  }    
   
  /* tries to do_builtin in the args */
  /* biexit is the global exit status value */
  biexit = do_builtin(argc, argv, cinfd, coutfd, cerrfd);
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
    if(cinfd != 0){
      if(dup2(cinfd, 0) == -1){
        perror("dup2 cinfd");
      }
    }
    if(coutfd != 1){
      if(dup2(coutfd, 1) == -1){
        perror("dup2 coutfd");
      }
    }
    if(cerrfd != 2){
      if(dup2(cerrfd, 2) == -1){
        perror("dup2 cerrfd");
      }
    }
    execvp (argv[0], argv);
    perror ("exec");
    free(argv);
    exit (127);
  }

  if(cinfd != infd){
    close(cinfd);
  }
  if(coutfd != outfd){
    close(coutfd);
  }
  if(cerrfd != 2){
    close(cerrfd);
  }


  /* Have the parent wait for child to complete */
  if(waitflag == yeswait){
    if(cpid > 0){
      if (waitpid(cpid, &status, 0) < 0)
        perror ("wait");
      if (WIFEXITED(status)){
        biexit = WEXITSTATUS(status);
      }
      else{
        biexit = 127;
      }
    }
  }

  return cpid;
}
