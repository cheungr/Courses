/*	$Id: arg_parse.c,v 1.5 2014/05/26 20:11:46 cheungr Exp $	*/

/* CS 352 -- Arg_Parse, part of the MiniShell!
 *
 *   Sept 21, 2000,  Phil Nelson
 *   Modified April 8, 2001
 *   Modified January 6, 2003
 *   Modified April 13, 2014 Roy Cheung
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "global.h"
#include "proto.h"

int arg_parse(char *line, char ***argvp)
{
  int argc = 0,
    i = 0,
    len = strlen(line),
    k = 0;
  char **argv;
  int quotes_c = 0;
  int state = 0;

  /* Awesome state machine to count arguments and quotes. */
  while (i < len){
    if(state == 0){
      if(line[i] == ' '){
        state = 0;
      }
      else if(line[i] == '\"'){
        state = 3;
        quotes_c++;
        argc++;
      }
      else{
        state = 1;
        argc++;
      }
    }
    else if(state == 1){
      if(line[i] == ' '){
        state = 0;
      }
      else if(line[i] == '\"'){
        state = 2;
        quotes_c++;
      }
    }
    else if(state == 2){
      if(line[i] == '\"'){
        state = 1;
        quotes_c++;
      }
    }
    else if(state == 3){
      if(line[i] == '\"'){
        state = 4;
        quotes_c++;
      }
      else{
        state = 2;
      }
    }
    else if(state == 4){
      if(line[i] == ' '){
        state = 0;
      }
      else if(line[i] == '\"'){
        state = 3;
        quotes_c++;
      }
      else{
        state = 1;
      }
    }
    i++;
  }

  /* checks for quote mismatches. */
  if (state == 2){
  	dprintf(2, "%s: unmatched quotes. \n" , mainargl[0]);
    return 0;
  }
  else if ((quotes_c % 2) != 0){
    dprintf(2, "%s: unmatched quotes. \n" , mainargl[0]);
  	return 0;
  }
  

  /* allocate memory for array of arguments */
  argv = (char **)malloc(sizeof(char *) * (argc + 1));
  if (!argv)
    perror("malloc");

  char *src = line;
  char *dst = line;

  /* Assigns pointers and sets space to 0 at end of argument */

  i = 0;
  state = 0;
  
  while (*src){
    if(state == 0){
      if(*src == ' '){
        state = 0;
      }
      else if(*src == '\"'){
        state = 3;
      }
      else{
        state = 1;
        *dst = *src;
        argv[k] = &*dst;
        dst++;
        k++;
      }
    }
    else if(state == 1){
      if(*src == ' '){
        state = 0;
        *src = '\0';
        *dst = *src;
        dst++;
      }
      else if(*src == '\"'){
        state = 2;
      }
      else{
        *dst = *src;
        dst++;
      }
    }
    else if(state == 2){
      if(*src == '\"'){
        state = 1;
      }
      else{
        *dst = *src;
        dst++;
      }
    }
    else if(state == 3){
      if(*src == '\"'){
        state = 4;
      }
      else{
        state = 2;
        *dst = *src;
        argv[k] = &*dst;
        dst++;
        k++;
      }
    }
    else if(state == 4){
      if(*src == ' '){
        *src = '\0';
        *dst = *src;
        argv[k] = &*dst;
        dst++;
        k++;
        state = 0;
      }
      else if(*src == '\"'){
        state = 3;
      }
      else{
        *dst = *src;
        dst++;
        state = 1;
      }
    }
    src++;
  }

  /* Sets 0 for end of the last argument. */
  *src = '\0';
  *dst = *src;
  argv[k] = &*dst;

  /* Sets NULL pointer */
  argv[argc] = NULL;
  
  *argvp = argv;

  return argc;
}
