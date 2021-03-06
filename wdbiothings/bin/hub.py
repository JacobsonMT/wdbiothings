#!/usr/bin/env python

import asyncio, asyncssh, sys
import concurrent.futures
from functools import partial

from wdbiothings import config
import biothings
biothings.config_for_app(config)

from biothings.utils.manager import JobManager
loop = asyncio.get_event_loop()
process_queue = concurrent.futures.ProcessPoolExecutor()#max_workers=2)
thread_queue = concurrent.futures.ThreadPoolExecutor()
loop.set_default_executor(process_queue)
jmanager = JobManager(loop,
                      process_queue, thread_queue,
                      max_memory_usage="auto",
                      )


from wdbiothings import contrib
import biothings.dataload.uploader as uploader
import biothings.dataload.dumper as dumper

# will check every 10 seconds for sources to upload
umanager = uploader.UploaderManager(poll_schedule='* * * * * */10', job_manager=jmanager)
umanager.register_sources(contrib.__sources_dict__)
umanager.poll()

dmanager = dumper.DumperManager(job_manager=jmanager)
dmanager.register_sources(contrib.__sources_dict__)
dmanager.schedule_all()


from biothings.utils.hub import schedule, top, pending, done

COMMANDS = {
        # dump commands
        "dm" : dmanager,
        "dump" : dmanager.dump_src,
        "dump_all" : dmanager.dump_all,
        # upload commands
        "um" : umanager,
        "upload" : umanager.upload_src,
        "upload_all": umanager.upload_all,
        # admin/advanced
        "loop" : loop,
        "pqueue" : process_queue,
        "tqueue" : thread_queue,
        "g": globals(),
        "sch" : partial(schedule,loop),
        "top" : partial(top,process_queue,thread_queue),
        "pending" : pending,
        "done" : done,
        }

passwords = {
        'guest': '', # guest account with no password
        }

from biothings.utils.hub import start_server

server = start_server(loop, "wikidata hub",passwords=passwords,port=8022,commands=COMMANDS)

try:
    loop.run_until_complete(server)
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()
