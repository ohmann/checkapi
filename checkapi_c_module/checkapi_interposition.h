/* Author: Jerome Yang Li 
 * File: checkapi_interposition.c
 * Purpose: For checkapi interposition
 */

#include "Python.h"
#include <stdio.h>   
#include <string.h>  
#include <stdlib.h>  
#include <sys/types.h>
#include <sys/socket.h>    
#include <arpa/inet.h>     
#include <unistd.h>        


static void send_data(void *data);
static PyObject *SetStringData(PyObject* self, PyObject* args);
static PyObject *CreateConnectSocket(PyObject* self);
static PyObject *CloseSocket(PyObject* self);

