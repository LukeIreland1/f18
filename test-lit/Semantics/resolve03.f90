!RUN: %S/test_errors.sh %s %flang
implicit none
integer :: x
!ERROR: No explicit type declared for 'y'
y = x
end
