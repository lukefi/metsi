*** Settings ***
Library    OperatingSystem
Library    Process


*** Test Cases ***
Run Command With Help Option
    [Tags]         smoke
    
    ${env} =       Get Environment Variables
    ${result} =    Run Process    python
    ...            -m
    ...            lukefi.metsi.app.metsi
    ...            -h
    ...            shell=True

    Log    STDOUT:\n${result.stdout}
    Log    STDERR:\n${result.stderr}

    Should Be Equal As Integers    ${result.rc}    0
    ...    msg=Python script failed! See STDERR log for details.