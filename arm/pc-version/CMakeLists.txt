# trying this out...
cmake_minimum_required(VERSION 2.6)

# name project
project(pc-armMon)


set(CMAKE_BUILD_TYPE Debug)
add_executable(pc-armMon pc-main.c monitor.c circbuf.c genmonconfig.c)
