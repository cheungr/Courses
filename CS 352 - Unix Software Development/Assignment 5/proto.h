/*	$Id: proto.h,v 1.4 2014/05/26 20:11:46 cheungr Exp $	*/

/* CS 352 -- Mini Shell! proto.h
 *
 *
 * April 14, 2014 - Roy Cheung
 * Modified April 26, 2014 
 *
 */

int arg_parse(char *line, char ***argvp);
int do_builtin (int argc, char **argvp, int outfd);
int expand (char *orig, char *new, int newsize);
int processline (char *line, int outfd, int waitflag);