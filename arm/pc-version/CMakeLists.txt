# trying this out...
cmake_minimum_required(VERSION 2.6)
# name project
project(pc-armMon)
add_executable(pc-armMon main.c monitor.c circbuf.c genmonconfig.c)
