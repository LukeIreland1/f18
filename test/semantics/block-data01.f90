! Test BLOCK DATA subprogram (14.3)
block data foo
  !ERROR: IMPORT is not allowed in a BLOCK DATA subprogram
  import
  real :: pi = asin(-1.0) ! ok
  !ERROR: An initialized variable in BLOCK DATA must be in a COMMON block
  integer :: notInCommon = 1
  integer :: uninitialized ! ok
  !ERROR: 'p' may not appear in a BLOCK DATA subprogram
  procedure(sin), pointer :: p => cos
  !ERROR: 'p' is already declared as a procedure
  common /block/ pi, p
  real :: inBlankCommon
  data inBlankCommon / 1.0 /
  common inBlankCommon
  !ERROR: An initialized variable in BLOCK DATA must be in a COMMON block
  integer :: inDataButNotCommon
  data inDataButNotCommon / 1 / 
end block data