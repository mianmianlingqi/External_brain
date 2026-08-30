# Serve starts before Init

A server Target process must listen without a first Direction. Init (`expand`) happens after the process is up. Requiring `FIRST_DIRECTION` at process start is rejected.
