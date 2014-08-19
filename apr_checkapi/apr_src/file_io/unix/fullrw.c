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

#include "apr_file_io.h"

#include "aprtrace.h"
#include "apr_arch_file_io.h"   // Required for apr_file_t defn for tracing



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_read_full_log(apr_file_t *thefile, void *buf,
                                             apr_size_t nbytes,
                                             apr_size_t *bytes_read,
                                             int is_direct)
{
  int ret = apr_file_read_full_(thefile, buf, nbytes, bytes_read);
  write_type_and_func("int", "apr_file_read_full", is_direct);
  write_int(thefile==NULL ? NULLINT : thefile->filedes);
  // skip buf
  write_int(nbytes);
  write_int_ret_arg(bytes_read==NULL ? NULLINT : *bytes_read);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_read_full(apr_file_t *thefile, void *buf,
                                             apr_size_t nbytes,
                                             apr_size_t *bytes_read)
{
  return apr_file_read_full_log(thefile, buf, nbytes, bytes_read, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_read_full_(apr_file_t *thefile, void *buf,
                                             apr_size_t nbytes,
                                             apr_size_t *bytes_read)
{
    apr_status_t status;
    apr_size_t total_read = 0;

    do {
	apr_size_t amt = nbytes;

	status = apr_file_read_log(thefile, buf, &amt, NESTED);
	buf = (char *)buf + amt;
        nbytes -= amt;
        total_read += amt;
    } while (status == APR_SUCCESS && nbytes > 0);

    if (bytes_read != NULL)
        *bytes_read = total_read;

    return status;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_write_full_log(apr_file_t *thefile,
                                              const void *buf,
                                              apr_size_t nbytes,
                                              apr_size_t *bytes_written,
                                              int is_direct)
{
  int ret = apr_file_write_full_(thefile, buf, nbytes, bytes_written);
  write_type_and_func("int", "apr_file_write_full", is_direct);
  write_int(thefile==NULL ? NULLINT : thefile->filedes);
  // skip buf
  write_int(nbytes);
  write_int_ret_arg(bytes_written==NULL ? NULLINT : *bytes_written);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_write_full(apr_file_t *thefile,
                                              const void *buf,
                                              apr_size_t nbytes,
                                              apr_size_t *bytes_written)
{
  return apr_file_write_full_log(thefile, buf, nbytes, bytes_written, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_write_full_(apr_file_t *thefile,
                                              const void *buf,
                                              apr_size_t nbytes,
                                              apr_size_t *bytes_written)
{
    apr_status_t status;
    apr_size_t total_written = 0;

    do {
	apr_size_t amt = nbytes;

	status = apr_file_write_log(thefile, buf, &amt, NESTED);
	buf = (char *)buf + amt;
        nbytes -= amt;
        total_written += amt;
    } while (status == APR_SUCCESS && nbytes > 0);

    if (bytes_written != NULL)
        *bytes_written = total_written;

    return status;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_writev_full_log(apr_file_t *thefile,
                                               const struct iovec *vec,
                                               apr_size_t nvec,
                                               apr_size_t *bytes_written,
                                               int is_direct)
{
  int ret = apr_file_writev_full_(thefile, vec, nvec, bytes_written);
  write_type_and_func("int", "apr_file_writev_full", is_direct);
  write_int(thefile==NULL ? NULLINT : thefile->filedes);
  // skip iovec
  write_int(nvec);
  write_int_ret_arg(bytes_written==NULL ? NULLINT : *bytes_written);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_writev_full(apr_file_t *thefile,
                                               const struct iovec *vec,
                                               apr_size_t nvec,
                                               apr_size_t *bytes_written)
{
  return apr_file_writev_full_log(thefile, vec, nvec, bytes_written, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_writev_full_(apr_file_t *thefile,
                                               const struct iovec *vec,
                                               apr_size_t nvec,
                                               apr_size_t *bytes_written)
{
    apr_status_t rv = APR_SUCCESS;
    apr_size_t i;
    apr_size_t amt = 0;
    apr_size_t total = 0;

    for (i = 0; i < nvec; i++) {
        total += vec[i].iov_len;
    }

    rv = apr_file_writev_log(thefile, vec, nvec, &amt, NESTED);

    if (bytes_written != NULL)
        *bytes_written = amt;

    if (rv != APR_SUCCESS || (amt == total)) {
        return rv;
    }

    for (i = 0; i < nvec && amt; i++) {
        if (amt >= vec[i].iov_len) {
            amt -= vec[i].iov_len;
        }
        else {
            break;
        }
    }

    if (amt) {
        rv = apr_file_write_full_log(thefile, (const char *)vec[i].iov_base + amt,
                                 vec[i].iov_len - amt, NULL, NESTED);
    }

    for (; i < nvec && rv == APR_SUCCESS; i++) {
        rv = apr_file_write_full_log(thefile, vec[i].iov_base,
                                 vec[i].iov_len, &amt, NESTED);
    }

    if (bytes_written != NULL)
        *bytes_written = total;

    return rv;
}
