/*
 * Author Savvas Savvides
 * Date 12-12-12
 * 
 * Run system calls
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "syscalls.h"
#include "syscalls_functions.h"


/*
 * This function lists all implemented system calls in stdout.
 * 
 */
void list_syscalls() 
{
  int i, implemented = 0;

  fprintf(stdout, "Implemented System Calls\n");
  for(i=0; i<SYSCALLS_LENGTH; i++)
    if(SYSCALLS[i].implemented == 1)
      fprintf(stdout, "%3d: %s\n", ++implemented, SYSCALLS[i].name);
  fprintf(stdout, "\n %d out of %d system calls implemented.\n"
                  , implemented, SYSCALLS_LENGTH);
} // list_syscalls

/*
 * This function produces a usage help message.
 * 
 * 
 */
void usage_help(char *argv[]) 
{
  fprintf(stdout, "Usage:\n");
  fprintf(stdout, "%s list -- list all implemented system calls.\n",
          argv[0]);
  fprintf(stdout, "%s syscall_name -- execute specific system call.\n",
          argv[0]);
} // usage_help


/*
 * This function checks if the given comamnd line arguments are
 * valid and decides which system calls are to be executed.
 *
 */
int validate_arguments(int argc, char *argv[]) 
{
  if(argc < 2) 
  {
    // if no command line arguments are given
    // print a message and exit.
    fprintf(stderr, "%s: missing arguments\n", argv[0]);
    fprintf(stderr, "Try `%s help' for more information\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  else if(strcmp(argv[1], "help") == 0) 
  {
    // if the first command line argument is "help"
    // print usage help.
    usage_help(argv);
    exit(EXIT_SUCCESS);
  }
  else if(strcmp(argv[1], "list") == 0) 
  {
    // if the first command line argument is "list"
    // system calls dealt with must be listed
    return -1;
  }
  else 
  {
    // check if the first command line argument matches one of the 
    // system calls.
    int i;
    for(i=0; i<SYSCALLS_LENGTH; i++)
      if(strcmp(argv[1], SYSCALLS[i].name) == 0)
        return i;
    
    // command not known.
    fprintf(stderr, "%s: invalid option -- '%s'\n", argv[0], argv[1]);
    fprintf(stderr, "Try `%s help' for more information\n", argv[0]);
    exit(EXIT_FAILURE);
  }
} // validate_arguments


int main(int argc, char *argv[]) 
{
  // validate given arguments and return the type of action to be
  // performed.
  int action_choice = validate_arguments(argc, argv);
  
  if(action_choice == -1) 
  {
    // -2 indicates the list action. 
    list_syscalls();
  }
  else if(action_choice >= 0 && action_choice < SYSCALLS_LENGTH)
  {
    // execute specific system call.
    if(SYSCALLS[action_choice].implemented == 1)
      SYSCALLS[action_choice].f();
    else 
    {
      fprintf(stderr, "%s: System call `%s' not implemented.\n"
                      , argv[0], SYSCALLS[action_choice].name);
      fprintf(stderr, "Try `%s list' to see a list of "
                      "system calls implemented.\n", argv[0]);
      exit(EXIT_FAILURE);
    }
  }
  else 
  {
    fprintf(stderr, "%s: Unexpected case occured.\n", argv[0]);
    fprintf(stderr, "Try `%s help' for more information\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  
  return 0;
}
