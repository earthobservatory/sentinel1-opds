#!/usr/bin/env python

from builtins import str
import os, sys, time, json, requests, logging, traceback
import acquisition_localizer_multi

def main():

    
    context_file = os.path.abspath("_context.json")
    if not os.path.exists(context_file):
        raise RuntimeError
    acquisition_localizer_multi.resolve_source(context_file)

if __name__ == '__main__':
    try: status = main()
    except Exception as e:
        with open('_alt_error.txt', 'w') as f:
            f.write("%s\n" % str(e))
        with open('_alt_traceback.txt', 'w') as f:
            f.write("%s\n" % traceback.format_exc())
        raise
    sys.exit(status)
