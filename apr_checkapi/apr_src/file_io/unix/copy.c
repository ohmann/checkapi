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
#include "apr_file_io.h"

#include "aprtrace.h"

static apr_status_t apr_file_transfer_contents(const char *from_path,
                                               const char *to_path,
                                               apr_int32_t flags,
                                               apr_fileperms_t to_perms,
                                               apr_pool_t *pool)
{
    apr_file_t *s, *d;
    apr_status_t status;
    apr_finfo_t finfo;
    apr_fileperms_t perms;

    /* Open source file. */
    status = apr_file_open_log(&s, from_path, APR_FOPEN_READ, APR_OS_DEFAULT, pool, NESTED);
    if (status)
        return status;

    /* Maybe get its permissions. */
    if (to_perms == APR_FILE_SOURCE_PERMS) {
        status = apr_file_info_get_log(&finfo, APR_FINFO_PROT, s, NESTED);
        if (status != APR_SUCCESS && status != APR_INCOMPLETE) {
            apr_file_close_log(s, NESTED);  /* toss any error */
            return status;
        }
        perms = finfo.protection;
    }
    else
        perms = to_perms;

    /* Open dest file. */
    status = apr_file_open_log(&d, to_path, flags, perms, pool, NESTED);
    if (status) {
        apr_file_close_log(s, NESTED);  /* toss any error */
        return status;
    }

#if BUFSIZ > APR_FILE_DEFAULT_BUFSIZE
#define COPY_BUFSIZ BUFSIZ
#else
#define COPY_BUFSIZ APR_FILE_DEFAULT_BUFSIZE
#endif

    /* Copy bytes till the cows come home. */
    while (1) {
        char buf[COPY_BUFSIZ];
        apr_size_t bytes_this_time = sizeof(buf);
        apr_status_t read_err;
        apr_status_t write_err;

        /* Read 'em. */
        read_err = apr_file_read_log(s, buf, &bytes_this_time, NESTED);
        if (read_err && !APR_STATUS_IS_EOF(read_err)) {
            apr_file_close_log(s, NESTED);  /* toss any error */
            apr_file_close_log(d, NESTED);  /* toss any error */
            return read_err;
        }

        /* Write 'em. */
        write_err = apr_file_write_full_log(d, buf, bytes_this_time, NULL, NESTED);
        if (write_err) {
            apr_file_close_log(s, NESTED);  /* toss any error */
            apr_file_close_log(d, NESTED);  /* toss any error */
            return write_err;
        }

        if (read_err && APR_STATUS_IS_EOF(read_err)) {
            status = apr_file_close_log(s, NESTED);
            if (status) {
                apr_file_close_log(d, NESTED);  /* toss any error */
                return status;
            }

            /* return the results of this close: an error, or success */
            return apr_file_close_log(d, NESTED);
        }
    }
    /* NOTREACHED */
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_copy_log(const char *from_path,
                                        const char *to_path,
                                        apr_fileperms_t perms,
                                        apr_pool_t *pool,
                                        int is_direct)
{
  int ret = apr_file_copy_(from_path, to_path, perms, pool);
  write_type_and_func("int", "apr_file_copy", is_direct);
  write_string(from_path);
  write_string(to_path);
  write_int(perms);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_copy(const char *from_path,
                                        const char *to_path,
                                        apr_fileperms_t perms,
                                        apr_pool_t *pool)
{
  return apr_file_copy_log(from_path, to_path, perms, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_copy_(const char *from_path,
                                        const char *to_path,
                                        apr_fileperms_t perms,
                                        apr_pool_t *pool)
{
    return apr_file_transfer_contents(from_path, to_path,
                                      (APR_FOPEN_WRITE | APR_FOPEN_CREATE | APR_FOPEN_TRUNCATE),
                                      perms,
                                      pool);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_append_log(const char *from_path,
                                          const char *to_path,
                                          apr_fileperms_t perms,
                                          apr_pool_t *pool,
                                          int is_direct)
{
  int ret = apr_file_append_(from_path, to_path, perms, pool);
  write_type_and_func("int", "apr_file_append", is_direct);
  write_string(from_path);
  write_string(to_path);
  write_int(perms);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_append(const char *from_path,
                                          const char *to_path,
                                          apr_fileperms_t perms,
                                          apr_pool_t *pool)
{
  return apr_file_append_log(from_path, to_path, perms, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_append_(const char *from_path,
                                          const char *to_path,
                                          apr_fileperms_t perms,
                                          apr_pool_t *pool)
{
    return apr_file_transfer_contents(from_path, to_path,
                                      (APR_FOPEN_WRITE | APR_FOPEN_CREATE | APR_FOPEN_APPEND),
                                      perms,
                                      pool);
}
