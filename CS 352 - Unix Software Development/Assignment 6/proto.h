/*	$Id: proto.h,v 1.6 2014/06/05 22:23:19 cheungr Exp $	*/

/* CS 352 -- Mini Shell! proto.h
 *
 *
 * April 14, 2014 - Roy Cheung
 * Modified April 26, 2014 
 *
 */

int arg_parse(char *line, char ***argvp);
int do_builtin (int argc, char **argvp, int bi_infd, int bi_outfd, int bi_cerrfd);
int expand (char *orig, char *new, int newsize);
int processline (char *line, int infd, int outfd, int waitflag, int expandflag);