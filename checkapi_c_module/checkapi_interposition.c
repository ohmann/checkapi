/* Author: Jerome Yang Li 
 * File: checkapi_interposition.c
 * Purpose: For checkapi interposition
 */

#include "Python.h"
#include "checkapi_interposition.h"

static char* data_buffer = NULL;
static int offset_data_buffer = 0;
static int checkapi_socket = 0;                      
#define SIZE_DATA_BUFFER (1024*1024*4)    /* Memory size */

static void send_data(void *data){

  int rest_data_length = strlen(data);
  char* offset_send_data = data + strlen(data) - rest_data_length;     
  
  while (rest_data_length > 0) {
     offset_send_data = data + strlen(data) - rest_data_length; 
     rest_data_length -= send(checkapi_socket, offset_send_data, strlen(offset_send_data), 0);
  }
}

static PyObject *CreateConnectSocket(PyObject* self){

    struct sockaddr_in servAddr;  
    unsigned short servPort;      
    char *servIP;                     
    
    // Use loop-back IP address
    servIP = "127.0.0.1";
             
    // set port number
    servPort = atoi("50001");     
    
    // Create TCP socket
    if ((checkapi_socket = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
        printf("Error occur in socket()\n");

    memset(&servAddr, 0, sizeof(servAddr));     
    servAddr.sin_family      = AF_INET;             
    servAddr.sin_addr.s_addr = inet_addr(servIP);   
    servAddr.sin_port        = htons(servPort); 

    // Establish the connection 
    if (connect(checkapi_socket, (struct sockaddr *) &servAddr, sizeof(servAddr)) < 0)
        printf("Error occur in connect()\n");

    return Py_BuildValue("");
}

static PyObject *CloseSocket(PyObject* self){
	
    close(checkapi_socket);
    return Py_BuildValue("");
}


static PyObject *SetStringData(PyObject* self, PyObject* args)
{
    if (data_buffer == NULL) {
        data_buffer = (char*)malloc(SIZE_DATA_BUFFER * sizeof(char)); 
        memset(data_buffer, 0x00, SIZE_DATA_BUFFER * sizeof(char));
    }
    
    char *fromPython;
    if(!PyArg_Parse(args, "(s)", &fromPython)) {
        return NULL;
    }

    if (offset_data_buffer + strlen(fromPython) >= SIZE_DATA_BUFFER) {
        send_data(data_buffer);
        offset_data_buffer = 0;   
    } 

    memcpy(data_buffer + offset_data_buffer, fromPython, strlen(fromPython));
    offset_data_buffer += strlen(fromPython);

    return Py_BuildValue("");
}


/*
 * Bind Python function names to our C functions
 */
static PyMethodDef checkapi_interposition_methods[] = {
        {"CreateConnectSocket", CreateConnectSocket, METH_NOARGS, "Create and Connect Socket"},
        {"CloseSocket", CloseSocket, METH_NOARGS, "Close Socket"},
	{"SetStringData", SetStringData, METH_VARARGS, "Receive String"},
	{NULL, NULL, 0, NULL}
};


/*
 * Python calls this to let us initialize our module
 */
PyMODINIT_FUNC initcheckapi_interposition(void) {
  Py_InitModule("checkapi_interposition", checkapi_interposition_methods);
}

