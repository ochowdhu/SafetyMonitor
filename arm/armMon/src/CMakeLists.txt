# trying this out...
cmake_minimum_required(VERSION 2.6)

# name project
project(pc-armMon)


set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -lrt")
add_executable(pc-armMon pc-main.c monitor.c circbuf.c genmonconfig.c)
