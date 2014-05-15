/*    $Id: global.h,v 1.2 2014/05/09 03:45:20 cheungr Exp $    */
/* CS 352 -- Mini Shell!
 * 
 *	May 5, 2014 by Roy Cheung
 *	This is global file for automatic extern in non mainshell files.
 */

#ifdef MAINSHELL
	int mainargn;
	char **mainargl;
	int shift = 0;
	int biexit = 0;
	
#else
	extern int mainargn;
	extern char **mainargl;
	extern int shift;
	extern int biexit;
	
#endif
