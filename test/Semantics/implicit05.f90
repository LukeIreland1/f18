!RUN: %S/test_errors.sh %s %flang
subroutine s
  !ERROR: 'a' does not follow 'b' alphabetically
  implicit integer(b-a)
end
