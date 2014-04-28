/*	$Id: proto.h,v 1.3 2014/04/27 21:51:45 cheungr Exp $	*/

/* CS 352 -- Mini Shell! proto.h
 *
 *
 * April 14, 2014 - Roy Cheung
 * Modified April 26, 2014 
 *
 */

int arg_parse(char *line, char ***argvp);
int do_builtin (int argc, char **argvp);
int expand (char *orig, char *new, int newsize);
