#===-- test/Semantics/CMakeLists.txt ---------------------------------------===#
#
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
#===------------------------------------------------------------------------===#

# Run tests with test_errors.sh. It compiles the test with f18 and compares
# actual errors produced with expected ones listed in the source.

# These test files have expected errors in the source
set(ERROR_TESTS
)

# These test files have expected symbols in the source
set(SYMBOL_TESTS
)

# These test files have expected .mod file contents in the source
set(MODFILE_TESTS
  modfile09-*.f90
)

set(LABEL_TESTS
  label*.[Ff]90
)

set(DOCONCURRENT_TESTS
)

set(CANONDO_TESTS
  canondo*.[Ff]90
)

set(CRITICAL_TESTS
)

set(F18 $<TARGET_FILE:f18>)

foreach(test ${ERROR_TESTS})
  add_test(NAME ${test}
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/test_errors.sh ${test} ${F18})
endforeach()

foreach(test ${SYMBOL_TESTS})
  add_test(NAME ${test}
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/test_symbols.sh ${test} ${F18})
endforeach()

foreach(test ${MODFILE_TESTS})
  add_test(NAME ${test}
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/test_modfile.sh ${test} ${F18})
endforeach()

foreach(test ${LABEL_TESTS} ${CANONDO_TESTS} ${DOCONCURRENT_TESTS}
             ${CRITICAL_TESTS})
  add_test(NAME ${test}
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/test_any.sh ${test} ${F18})
endforeach()
