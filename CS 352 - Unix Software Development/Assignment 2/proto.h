/* CS 352 -- Mini Shell! proto.h
 *
 *
 * April 14, 2014 - Roy Cheung
 * 
 *
 */

int arg_parse(char *line, char ***argvp);
int do_builtin (int argc, char **argvp);
