/*	$Id: scriptin.c,v 1.1 2014/06/06 16:58:25 cheungr Exp $	*/

/* CS 352 -- scriptin.c, part of the MiniShell!
 *
 *   Sept 21, 2000,  Phil Nelson
 *   Modified April 8, 2001
 *   Modified January 6, 2003
 *   Modified April 13, 2014 Roy Cheung
 */

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

struct line{
	enum {W_IF, W_WHILE, W_ELSE, W_END, W_OTHER} stmtkind;
	int elsend;
	char *cmd; 	
};

typedef struct {
  int *array;
  size_t used;
  size_t size;
} Array;

void initArray(Array *a, size_t initialSize) {
  a->array = (int *)malloc(initialSize * sizeof(int));
  a->used = 0;
  a->size = initialSize;
}

void insertArray(Array *a, int element) {
  if (a->used == a->size) {
    a->size *= 2;
    a->array = (int *)realloc(a->array, a->size * sizeof(int));
  }
  a->array[a->used++] = element;
}

void freeArray(Array *a) {
  free(a->array);
  a->array = NULL;
  a->used = a->size = 0;
}

int init(){
  //initialize the struct
  return 0;
}

int add_line(char *line){
  //add lines to structs
  //alines == nlines, realloc() to twice size
  //then use strdup(3)
  return 0;
}

int get_line(int index){
  //given index, get the line
  return 0;
}

//first_word()
//skip white space, keyword must be first, not in quotes
//return integer/enumerated struct in line, W_IF, etc.

//read_if() <- read until end of line, allowing at most one "else" line
// if statements, recurse

int read_stmt(int num_elses){
  //read until "end" line, allowing at most
  //num_elses "else" lines.
  //while (read_stmt(0), if (read_stmt(1))
  // Read_stmt ( line, s_kind, stmt_list)
  // stmt_index = stmt_list.Num_lines()
  // stmt_list.Add_line (s_kind,line)
  // num_elses = s_kind == W_IF ? 1 : 0
  // read a line into next_line
  // n_kind = first_word (next_line)
  // while n_kind != W_END
  // switch n_kind:
  // W_IF, W_WHILE: Read_stmt (next_line, n_kind, stmt_list)
  // W_ELSE: if num_elses > 0 {
  // stmt_list.Set_elsend(stmt_index, stmt_list.Num_lines())
  // stmt_index = stmt_list.Num_lines()
  // stmt_list.Add_line(next_line, W_ELSE);
  // num_elses--
  // } else { error }
  // W_OTHER: stmt_list.Add_line(next_line, W_OTHER)
  // end
  // read a line into next_line
  // n_kind = first_word (next_line)
  // end
  // stmt_list.Set_elsend(stmt_index, stmt_list.Num_lines())
  // stmt_list.Add_line(next_line, W_END)
  return 0;
}


