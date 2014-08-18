/* Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "apr_arch_file_io.h"
#include "apr_pools.h"
#include "apr_thread_mutex.h"

#include "aprtrace.h"



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_buffer_set_log(apr_file_t *file,
                                              char * buffer,
                                              apr_size_t bufsize,
                                              int is_direct)
{
  int ret = apr_file_buffer_set_(file, buffer, bufsize);
  write_type_and_func("int", "apr_file_buffer_set", is_direct);
  write_int(file==NULL ? NULLINT : file->filedes);
  // skip buffer
  write_int(bufsize);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_buffer_set(apr_file_t *file,
                                              char * buffer,
                                              apr_size_t bufsize)
{
  return apr_file_buffer_set_log(file, buffer, bufsize, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_buffer_set_(apr_file_t *file,
                                              char * buffer,
                                              apr_size_t bufsize)
{
    apr_status_t rv;

    file_lock(file);

    if(file->buffered) {
        /* Flush the existing buffer */
        rv = apr_file_flush_locked(file);
        if (rv != APR_SUCCESS) {
            file_unlock(file);
            return rv;
        }
    }

    file->buffer = buffer;
    file->bufsize = bufsize;
    file->buffered = 1;
    file->bufpos = 0;
    file->direction = 0;
    file->dataRead = 0;

    if (file->bufsize == 0) {
            /* Setting the buffer size to zero is equivalent to turning
             * buffering off.
             */
            file->buffered = 0;
    }

    file_unlock(file);

    return APR_SUCCESS;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_size_t) apr_file_buffer_size_get_(apr_file_t *file);
APR_DECLARE(apr_size_t) apr_file_buffer_size_get_log(apr_file_t *file,
                                                     int is_direct)
{
  int ret = apr_file_buffer_size_get_(file);
  write_type_and_func("int", "apr_file_buffer_size_get", is_direct);
  write_int(file==NULL ? NULLINT: file->filedes);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_size_t) apr_file_buffer_size_get(apr_file_t *file)
{
  return apr_file_buffer_size_get_log(file, DIRECT);
}



APR_DECLARE(apr_size_t) apr_file_buffer_size_get_(apr_file_t *file)
{
    return file->bufsize;
}
