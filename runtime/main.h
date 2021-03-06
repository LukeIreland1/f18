//===-- runtime/main.h ------------------------------------------*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef FORTRAN_RUNTIME_MAIN_H_
#define FORTRAN_RUNTIME_MAIN_H_

#include "c-or-cpp.h"
#include "entry-names.h"

FORTRAN_EXTERN_C_BEGIN
void RTNAME(ProgramStart)(int, const char *[], const char *[]);
FORTRAN_EXTERN_C_END

#endif  // FORTRAN_RUNTIME_MAIN_H_
