# trying this out...
cmake_minimum_required(VERSION 2.6)

# name project
project(pc-armMon)

#set(DO_MON_CONS OFF)
#set(DO_MON_AGGR OFF)
#option(DO_MON_CONS OFF)
#option(DO_MON_AGGR OFF)

if (DO_MON_CONS) 
	add_definitions("-D MON_TYPE -D MON_CONS")
	message(STATUS "building conservative monitor")
elseif (DO_MON_AGGR)
	add_definitions("-D MON_TYPE -D MON_AGGR")
	message(STATUS "building aggressive monitor")
else() #(DO_MON_BOTH)
	add_definitions("-D MON_TYPE -D MON_CONS -D MON_AGGR")
	message(STATUS "building cons/aggr monitor")
endif()	

set(CMAKE_BUILD_TYPE Debug)
if (CMAKE_HOST_LINUX)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -lrt")
endif()
add_definitions("-D PC_MODE")
add_executable(pc-armMon pc-main.c monitor.c circbuf.c genmonconfig.c)
