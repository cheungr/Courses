/*    $Id: global.h,v 1.6 2014/05/27 04:37:20 cheungr Exp $    */
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
	int waitjk = 0;
	int outfd = 0;
	int yeswait = 0;
	int nowait = 1;
	int mysig = 1;
	int globalsize = 200000;
	int epid = 0;
	
#else
	extern int mainargn;
	extern char **mainargl;
	extern int shift;
	extern int biexit;
	extern int waitjk;
	extern int yeswait;
	extern int nowait;
	extern int mysig;
	extern int globalsize;
	extern int epid;

#endif
