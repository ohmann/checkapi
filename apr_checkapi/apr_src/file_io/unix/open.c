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
#include "apr_strings.h"
#include "apr_portable.h"
#include "apr_thread_mutex.h"
#include "apr_arch_inherit.h"

#ifdef NETWARE
#include "nks/dirio.h"
#include "apr_hash.h"
#include "fsio.h"
#endif

#include "aprtrace.h"

static apr_status_t file_cleanup(apr_file_t *file, int is_child)
{
    apr_status_t rv = APR_SUCCESS;
    int fd = file->filedes;

    /* Set file descriptor to -1 before close(), so that there is no
     * chance of returning an already closed FD from apr_os_file_get().
     */
    file->filedes = -1;

    if (close(fd) == 0) {
        /* Only the parent process should delete the file! */
        if (!is_child && (file->flags & APR_FOPEN_DELONCLOSE)) {
            unlink(file->fname);
        }
#if APR_HAS_THREADS
        if (file->thlock) {
            rv = apr_thread_mutex_destroy(file->thlock);
        }
#endif
    }
    else {
        /* Restore, close() was not successful. */
        file->filedes = fd;

        /* Are there any error conditions other than EINTR or EBADF? */
        rv = errno;
    }
#ifndef WAITIO_USES_POLL
    if (file->pollset != NULL) {
        apr_status_t pollset_rv = apr_pollset_destroy(file->pollset);
        /* If the file close failed, return its error value,
         * not apr_pollset_destroy()'s.
         */
        if (rv == APR_SUCCESS) {
            rv = pollset_rv;
        }
    }
#endif /* !WAITIO_USES_POLL */
    return rv;
}

apr_status_t apr_unix_file_cleanup(void *thefile)
{
    apr_file_t *file = thefile;
    apr_status_t flush_rv = APR_SUCCESS, rv = APR_SUCCESS;

    if (file->buffered) {
        flush_rv = apr_file_flush_log(file, NESTED);
    }

    rv = file_cleanup(file, 0);

    return rv != APR_SUCCESS ? rv : flush_rv;
}

apr_status_t apr_unix_child_file_cleanup(void *thefile)
{
    return file_cleanup(thefile, 1);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_log(apr_file_t **new,
                                        const char *fname,
                                        apr_int32_t flag,
                                        apr_fileperms_t perm,
                                        apr_pool_t *pool,
                                        int is_direct)
{
  int ret = apr_file_open_(new, fname, flag, perm, pool);
  write_type_and_func("int", "apr_file_open", is_direct);
  write_int_ret_arg(new==NULL || *new==NULL ? NULLINT : (*new)->filedes);
  write_string(fname);
  write_int(flag);
  write_int(perm);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open(apr_file_t **new,
                                        const char *fname,
                                        apr_int32_t flag,
                                        apr_fileperms_t perm,
                                        apr_pool_t *pool)
{
  return apr_file_open_log(new, fname, flag, perm, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_(apr_file_t **new,
                                        const char *fname,
                                        apr_int32_t flag,
                                        apr_fileperms_t perm,
                                        apr_pool_t *pool)
{
    apr_os_file_t fd;
    int oflags = 0;
#if APR_HAS_THREADS
    apr_thread_mutex_t *thlock;
    apr_status_t rv;
#endif

    if ((flag & APR_FOPEN_READ) && (flag & APR_FOPEN_WRITE)) {
        oflags = O_RDWR;
    }
    else if (flag & APR_FOPEN_READ) {
        oflags = O_RDONLY;
    }
    else if (flag & APR_FOPEN_WRITE) {
        oflags = O_WRONLY;
    }
    else {
        return APR_EACCES;
    }

    if (flag & APR_FOPEN_CREATE) {
        oflags |= O_CREAT;
        if (flag & APR_FOPEN_EXCL) {
            oflags |= O_EXCL;
        }
    }
    if ((flag & APR_FOPEN_EXCL) && !(flag & APR_FOPEN_CREATE)) {
        return APR_EACCES;
    }

    if (flag & APR_FOPEN_APPEND) {
        oflags |= O_APPEND;
    }
    if (flag & APR_FOPEN_TRUNCATE) {
        oflags |= O_TRUNC;
    }
#ifdef O_BINARY
    if (flag & APR_FOPEN_BINARY) {
        oflags |= O_BINARY;
    }
#endif

    if (flag & APR_FOPEN_NONBLOCK) {
#ifdef O_NONBLOCK
        oflags |= O_NONBLOCK;
#else
        return APR_ENOTIMPL;
#endif
    }

#ifdef O_CLOEXEC
    /* Introduced in Linux 2.6.23. Silently ignored on earlier Linux kernels.
     */
    if (!(flag & APR_FOPEN_NOCLEANUP)) {
        oflags |= O_CLOEXEC;
}
#endif

#if APR_HAS_LARGE_FILES && defined(_LARGEFILE64_SOURCE)
    oflags |= O_LARGEFILE;
#elif defined(O_LARGEFILE)
    if (flag & APR_FOPEN_LARGEFILE) {
        oflags |= O_LARGEFILE;
    }
#endif

#if APR_HAS_THREADS
    if ((flag & APR_FOPEN_BUFFERED) && (flag & APR_FOPEN_XTHREAD)) {
        rv = apr_thread_mutex_create(&thlock,
                                     APR_THREAD_MUTEX_DEFAULT, pool);
        if (rv) {
            return rv;
        }
    }
#endif

    if (perm == APR_OS_DEFAULT) {
        fd = open(fname, oflags, 0666);
    }
    else {
        fd = open(fname, oflags, apr_unix_perms2mode(perm));
    }
    if (fd < 0) {
       return errno;
    }
    if (!(flag & APR_FOPEN_NOCLEANUP)) {
#ifdef O_CLOEXEC
        static int has_o_cloexec = 0;
        if (!has_o_cloexec)
#endif
        {
            int flags;

            if ((flags = fcntl(fd, F_GETFD)) == -1) {
                close(fd);
                return errno;
            }
            if ((flags & FD_CLOEXEC) == 0) {
                flags |= FD_CLOEXEC;
                if (fcntl(fd, F_SETFD, flags) == -1) {
                    close(fd);
                    return errno;
                }
            }
#ifdef O_CLOEXEC
            else {
                has_o_cloexec = 1;
            }
#endif
        }
    }

    (*new) = (apr_file_t *)apr_pcalloc(pool, sizeof(apr_file_t));
    (*new)->pool = pool;
    (*new)->flags = flag;
    (*new)->filedes = fd;

    (*new)->fname = apr_pstrdup(pool, fname);

    (*new)->blocking = BLK_ON;
    (*new)->buffered = (flag & APR_FOPEN_BUFFERED) > 0;

    if ((*new)->buffered) {
        (*new)->buffer = apr_palloc(pool, APR_FILE_DEFAULT_BUFSIZE);
        (*new)->bufsize = APR_FILE_DEFAULT_BUFSIZE;
#if APR_HAS_THREADS
        if ((*new)->flags & APR_FOPEN_XTHREAD) {
            (*new)->thlock = thlock;
        }
#endif
    }
    else {
        (*new)->buffer = NULL;
    }

    (*new)->is_pipe = 0;
    (*new)->timeout = -1;
    (*new)->ungetchar = -1;
    (*new)->eof_hit = 0;
    (*new)->filePtr = 0;
    (*new)->bufpos = 0;
    (*new)->dataRead = 0;
    (*new)->direction = 0;
#ifndef WAITIO_USES_POLL
    /* Start out with no pollset.  apr_wait_for_io_or_timeout() will
     * initialize the pollset if needed.
     */
    (*new)->pollset = NULL;
#endif
    if (!(flag & APR_FOPEN_NOCLEANUP)) {
        apr_pool_cleanup_register((*new)->pool, (void *)(*new),
                                  apr_unix_file_cleanup,
                                  apr_unix_child_file_cleanup);
    }
    return APR_SUCCESS;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_close_log(apr_file_t *file,
                                             int is_direct)
{
  // Filedes is lost after close, so record it here
  int file_before = (file==NULL ? NULLINT : file->filedes);
  int ret = apr_file_close_(file);
  write_type_and_func("int", "apr_file_close", is_direct);
  write_int(file_before);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_close(apr_file_t *file)
{
  return apr_file_close_log(file, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_close_(apr_file_t *file)
{
    return apr_pool_cleanup_run(file->pool, file, apr_unix_file_cleanup);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_remove_log(const char *path, apr_pool_t *pool,
                                              int is_direct)
{
  int ret = apr_file_remove_(path, pool);
  write_type_and_func("int", "apr_file_remove", is_direct);
  write_string(path);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_remove(const char *path, apr_pool_t *pool)
{
  return apr_file_remove_log(path, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_remove_(const char *path, apr_pool_t *pool)
{
    if (unlink(path) == 0) {
        return APR_SUCCESS;
    }
    else {
        return errno;
    }
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_rename_log(const char *from_path,
                                          const char *to_path,
                                          apr_pool_t *p,
                                          int is_direct)
{
  int ret = apr_file_rename_(from_path, to_path, p);
  write_type_and_func("int", "apr_file_rename", is_direct);
  write_string(from_path);
  write_string(to_path);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_rename(const char *from_path,
                                          const char *to_path,
                                          apr_pool_t *p)
{
  return apr_file_rename_log(from_path, to_path, p, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_rename_(const char *from_path,
                                          const char *to_path,
                                          apr_pool_t *p)
{
    if (rename(from_path, to_path) != 0) {
        return errno;
    }
    return APR_SUCCESS;
}

APR_DECLARE(apr_status_t) apr_os_file_get(apr_os_file_t *thefile,
                                          apr_file_t *file)
{
    *thefile = file->filedes;
    return APR_SUCCESS;
}

APR_DECLARE(apr_status_t) apr_os_file_put(apr_file_t **file,
                                          apr_os_file_t *thefile,
                                          apr_int32_t flags, apr_pool_t *pool)
{
    int *dafile = thefile;

    (*file) = apr_pcalloc(pool, sizeof(apr_file_t));
    (*file)->pool = pool;
    (*file)->eof_hit = 0;
    (*file)->blocking = BLK_UNKNOWN; /* in case it is a pipe */
    (*file)->timeout = -1;
    (*file)->ungetchar = -1; /* no char avail */
    (*file)->filedes = *dafile;
    (*file)->flags = flags | APR_FOPEN_NOCLEANUP;
    (*file)->buffered = (flags & APR_FOPEN_BUFFERED) > 0;

#ifndef WAITIO_USES_POLL
    /* Start out with no pollset.  apr_wait_for_io_or_timeout() will
     * initialize the pollset if needed.
     */
    (*file)->pollset = NULL;
#endif

    if ((*file)->buffered) {
        (*file)->buffer = apr_palloc(pool, APR_FILE_DEFAULT_BUFSIZE);
        (*file)->bufsize = APR_FILE_DEFAULT_BUFSIZE;
#if APR_HAS_THREADS
        if ((*file)->flags & APR_FOPEN_XTHREAD) {
            apr_status_t rv;
            rv = apr_thread_mutex_create(&((*file)->thlock),
                                         APR_THREAD_MUTEX_DEFAULT, pool);
            if (rv) {
                return rv;
            }
        }
#endif
    }
    return APR_SUCCESS;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_eof_log(apr_file_t *fptr,
                                           int is_direct)
{
  int ret = apr_file_eof_(fptr);
  write_type_and_func("int", "apr_file_eof", is_direct);
  write_int(fptr==NULL ? NULLINT : fptr->filedes);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_eof(apr_file_t *fptr)
{
  return apr_file_eof_log(fptr, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_eof_(apr_file_t *fptr)
{
    if (fptr->eof_hit == 1) {
        return APR_EOF;
    }
    return APR_SUCCESS;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_flags_stderr_log(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool,
                                                     int is_direct)
{
  int ret = apr_file_open_flags_stderr_(thefile, flags, pool);
  write_type_and_func("int", "apr_file_open_flags_stderr", is_direct);
  write_int_ret_arg(thefile==NULL || *thefile==NULL ? NULLINT : (*thefile)->filedes);
  write_int(flags);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open_flags_stderr(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool)
{
  return apr_file_open_flags_stderr_log(thefile, flags, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_flags_stderr_(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool)
{
    int fd = STDERR_FILENO;

    return apr_os_file_put(thefile, &fd, flags | APR_FOPEN_WRITE, pool);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_flags_stdout_log(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool,
                                                     int is_direct)
{
  int ret = apr_file_open_flags_stdout_(thefile, flags, pool);
  write_type_and_func("int", "apr_file_open_flags_stdout", is_direct);
  write_int_ret_arg(thefile==NULL || *thefile==NULL ? NULLINT : (*thefile)->filedes);
  write_int(flags);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open_flags_stdout(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool)
{
  return apr_file_open_flags_stdout_log(thefile, flags, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_flags_stdout_(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool)
{
    int fd = STDOUT_FILENO;

    return apr_os_file_put(thefile, &fd, flags | APR_FOPEN_WRITE, pool);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_flags_stdin_log(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool,
                                                     int is_direct)
{
  int ret = apr_file_open_flags_stdin_(thefile, flags, pool);
  write_type_and_func("int", "apr_file_open_flags_stdin", is_direct);
  write_int_ret_arg(thefile==NULL || *thefile==NULL ? NULLINT : (*thefile)->filedes);
  write_int(flags);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open_flags_stdin(apr_file_t **thefile,
                                                     apr_int32_t flags,
                                                     apr_pool_t *pool)
{
  return apr_file_open_flags_stdin_log(thefile, flags, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_flags_stdin_(apr_file_t **thefile,
                                                    apr_int32_t flags,
                                                    apr_pool_t *pool)
{
    int fd = STDIN_FILENO;

    return apr_os_file_put(thefile, &fd, flags | APR_FOPEN_READ, pool);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_stderr_log(apr_file_t **thefile,
                                               apr_pool_t *pool,
                                               int is_direct)
{
  int ret = apr_file_open_stderr_(thefile, pool);
  write_type_and_func("int", "apr_file_open_stderr", is_direct);
  write_int_ret_arg(thefile==NULL || *thefile==NULL ? NULLINT : (*thefile)->filedes);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open_stderr(apr_file_t **thefile,
                                               apr_pool_t *pool)
{
  return apr_file_open_stderr_log(thefile, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_stderr_(apr_file_t **thefile,
                                               apr_pool_t *pool)
{
    return apr_file_open_flags_stderr_log(thefile, 0, pool, NESTED);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_stdout_log(apr_file_t **thefile,
                                               apr_pool_t *pool,
                                               int is_direct)
{
  int ret = apr_file_open_stdout_(thefile, pool);
  write_type_and_func("int", "apr_file_open_stdout", is_direct);
  write_int_ret_arg(thefile==NULL || *thefile==NULL ? NULLINT : (*thefile)->filedes);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open_stdout(apr_file_t **thefile,
                                               apr_pool_t *pool)
{
  return apr_file_open_stdout_log(thefile, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_stdout_(apr_file_t **thefile,
                                               apr_pool_t *pool)
{
    return apr_file_open_flags_stdout_log(thefile, 0, pool, NESTED);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_open_stdin_log(apr_file_t **thefile,
                                               apr_pool_t *pool,
                                               int is_direct)
{
  int ret = apr_file_open_stdin_(thefile, pool);
  write_type_and_func("int", "apr_file_open_stdin", is_direct);
  write_int_ret_arg(thefile==NULL || *thefile==NULL ? NULLINT : (*thefile)->filedes);
  // skip pool
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_open_stdin(apr_file_t **thefile,
                                               apr_pool_t *pool)
{
  return apr_file_open_stdin_log(thefile, pool, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_open_stdin_(apr_file_t **thefile,
                                              apr_pool_t *pool)
{
    return apr_file_open_flags_stdin_log(thefile, 0, pool, NESTED);
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_inherit_set_log(apr_file_t *thefile,
                                                   int is_direct)
{
  int ret = apr_file_inherit_set_(thefile);
  write_type_and_func("int", "apr_file_inherit_set", is_direct);
  write_int(thefile==NULL ? NULLINT : thefile->filedes);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_inherit_set(apr_file_t *thefile)
{
  return apr_file_inherit_set_log(thefile, DIRECT);
}



// CHECKAPI note: manually expanded macro to greatly reduce logging confusion
APR_DECLARE(apr_status_t) apr_file_inherit_set_(apr_file_t *thefile)
{
    if (thefile->flags & APR_FOPEN_NOCLEANUP)
        return APR_EINVAL;
    if (!(thefile->flags & APR_INHERIT)) {
        int flags = fcntl(thefile->filedes, F_GETFD);
        if (flags == -1)
            return errno;
        flags &= ~(FD_CLOEXEC);
        if (fcntl(thefile->filedes, F_SETFD, flags) == -1)
            return errno;
        thefile->flags |= APR_INHERIT;
        apr_pool_child_cleanup_set(thefile->pool,
                                   (void *)thefile,
                                   apr_unix_file_cleanup, apr_pool_cleanup_null);
    }
    return APR_SUCCESS;
}



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_inherit_unset_log(apr_file_t *thefile,
                                                     int is_direct)
{
  int ret = apr_file_inherit_unset_(thefile);
  write_type_and_func("int", "apr_file_inherit_unset", is_direct);
  write_int(thefile==NULL ? NULLINT : thefile->filedes);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_inherit_unset(apr_file_t *thefile)
{
  return apr_file_inherit_unset_log(thefile, DIRECT);
}



/* We need to do this by hand instead of using APR_IMPLEMENT_INHERIT_UNSET
 * because the macro sets both cleanups to the same function, which is not
 * suitable on Unix (see PR 41119). */
APR_DECLARE(apr_status_t) apr_file_inherit_unset_(apr_file_t *thefile)
{
    if (thefile->flags & APR_FOPEN_NOCLEANUP) {
        return APR_EINVAL;
    }
    if (thefile->flags & APR_INHERIT) {
        int flags;

        if ((flags = fcntl(thefile->filedes, F_GETFD)) == -1)
            return errno;

        flags |= FD_CLOEXEC;
        if (fcntl(thefile->filedes, F_SETFD, flags) == -1)
            return errno;

        thefile->flags &= ~APR_INHERIT;
        apr_pool_child_cleanup_set(thefile->pool,
                                   (void *)thefile,
                                   apr_unix_file_cleanup,
                                   apr_unix_child_file_cleanup);
    }
    return APR_SUCCESS;
}

// CHECKAPI note: skipping pool_get because the model ignores pools

APR_POOL_IMPLEMENT_ACCESSOR(file)



// CHECKAPI SHIM FOR LOGGING
APR_DECLARE(apr_status_t) apr_file_link_log(const char *from_path,
                                          const char *to_path,
                                          int is_direct)
{
  int ret = apr_file_link_(from_path, to_path);
  write_type_and_func("int", "apr_file_link", is_direct);
  write_string(from_path);
  write_string(to_path);
  write_return_int(ret);
  return ret;
}

// CHECKAPI SHIM FOR LOGGING (direct call)
APR_DECLARE(apr_status_t) apr_file_link(const char *from_path,
                                          const char *to_path)
{
  return apr_file_link_log(from_path, to_path, DIRECT);
}



APR_DECLARE(apr_status_t) apr_file_link_(const char *from_path,
                                          const char *to_path)
{
    if (link(from_path, to_path) == -1) {
        return errno;
    }

    return APR_SUCCESS;
}
