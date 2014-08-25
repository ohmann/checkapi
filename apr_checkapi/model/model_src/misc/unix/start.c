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

#include "apr.h"
#include "apr_general.h"
#include "apr_pools.h"
#include "apr_signal.h"
#include "apr_atomic.h"

#include "apr_arch_proc_mutex.h" /* for apr_proc_mutex_unix_setup_lock() */
#include "apr_arch_internal_time.h"



// BEGIN CHECKAPI COMMON MODEL CODE
#include "checkapicommon.h"

void set_py_functions(int (oracle_get_id_)(void),
                      int (oracle_getter_)(int, char*),
                      int (fs_fcntl2_)(int, int),
                      int (fs_fcntl3_)(int, int, int),
                      int (fs_dup_)(int),
                      int (fs_dup2_)(int, int),
                      int (fs_open_)(char*, int, int),
                      int (fs_close_)(int),
                      int (fs_unlink_)(char*),
                      void (*set_errno_)(int),
                      int (*get_errno_)(void)) {
  oracle_get_id = oracle_get_id_;
  oracle_getter = oracle_getter_;
  fs_fcntl2 = fs_fcntl2_;
  fs_fcntl3 = fs_fcntl3_;
  fs_dup = fs_dup_;
  fs_dup2 = fs_dup2_;
  fs_open = fs_open_;
  fs_close = fs_close_;
  fs_unlink = fs_unlink_;
  set_errno = set_errno_;
  get_errno = get_errno_;
}
// END CHECKAPI COMMON MODEL CODE



APR_DECLARE(apr_status_t) apr_app_initialize(int *argc,
                                             const char * const * *argv,
                                             const char * const * *env)
{
    /* An absolute noop.  At present, only Win32 requires this stub, but it's
     * required in order to move command arguments passed through the service
     * control manager into the process, and it's required to fix the char*
     * data passed in from win32 unicode into utf-8, win32's apr internal fmt.
     */
    return apr_initialize();
}

static int initialized = 0;

APR_DECLARE(apr_status_t) apr_initialize(void)
{
    apr_pool_t *pool;
    apr_status_t status;

    if (initialized++) {
        return APR_SUCCESS;
    }

#if !defined(BEOS) && !defined(OS2)
    apr_proc_mutex_unix_setup_lock();
    apr_unix_setup_time();
#endif

    if ((status = apr_pool_initialize()) != APR_SUCCESS)
        return status;

    if (apr_pool_create(&pool, NULL) != APR_SUCCESS) {
        return APR_ENOPOOL;
    }

    apr_pool_tag(pool, "apr_initialize");

    /* apr_atomic_init() used to be called from here aswell.
     * Pools rely on mutexes though, which can be backed by
     * atomics.  Due to this circular dependency
     * apr_pool_initialize() is taking care of calling
     * apr_atomic_init() at the correct time.
     */

    apr_signal_init(pool);

    return APR_SUCCESS;
}

APR_DECLARE_NONSTD(void) apr_terminate(void)
{
    initialized--;
    if (initialized) {
        return;
    }
    apr_pool_terminate();

}

APR_DECLARE(void) apr_terminate2(void)
{
    apr_terminate();
}
