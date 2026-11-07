cmake_minimum_required(VERSION 3.20)
project(clang_split_corpus CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
option(DEMO_FEATURE "Build the optional feature branch" ON)
option(DEMO_TESTING "Build testing probes" OFF)
add_executable(demo
	src/main.cpp
	src/catalog.cpp
	src/widget.cpp
)
target_include_directories(demo PRIVATE src)
if(DEMO_FEATURE)
	target_compile_definitions(demo PRIVATE DEMO_FEATURE=1)
endif()
if(DEMO_TESTING)
	target_compile_definitions(demo PRIVATE DEMO_TESTING=1)
endif()
