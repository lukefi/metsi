*** Settings ***
Library           OperatingSystem
Library           Process
Library           Collections
Library           String
Library           ${CURDIR}/../CustomCompareLibrary.py

*** Variables ***
${SCRIPT}           -m
${MODULE}           lukefi.metsi.app.metsi
${INPUT_JSON}       ${CURDIR}/input/demo.json
${OUTPUT_DIR}       ${CURDIR}/output/test
${CONTROL_SCRIPT}   ${CURDIR}/input/demo_control_sim2.py
${REFERENCE_DIR}    ${CURDIR}/output/ref
${TOLERANCE}        0.01  # Set your desired tolerance here

*** Test Cases ***
Run Simulation And Compare Output Files
    [Tags]    simulation

    Remove Directory    ${OUTPUT_DIR}    recursive=True
    Create Directory    ${OUTPUT_DIR}

    Log To Console    \n--- DEBUGGING ---
    Log To Console    Current Directory: ${CURDIR}
    Log To Console    Input JSON Path: ${INPUT_JSON}
    Log To Console    Output Dir Path: ${OUTPUT_DIR}
    Log To Console    Running Module:  ${MODULE}
    Log To Console    -----------------\n

    ${orig_env}=    Get Environment Variables
    Set To Dictionary    ${orig_env}    PYTHONPATH=${EXECDIR}
    ${result}=    Run Process    python
    ...           ${SCRIPT}
    ...           ${MODULE}
    ...           ${INPUT_JSON}
    ...           ${OUTPUT_DIR}
    ...           ${CONTROL_SCRIPT}
    ...           shell=True
    ...           stdout=YES
    ...           stderr=YES
    ...           env=${orig_env}

    Log    STDOUT:\n${result.stdout}
    Log    STDERR:\n${result.stderr}

    Should Be Equal As Integers    ${result.rc}    0    msg=Python script failed! See STDERR log for details.

    Log To Console    Simulation Succeeded. Verifying output files...

    ${files}=    List Directory    ${REFERENCE_DIR}
    FOR    ${file}    IN    @{files}
        ${test_file}=    Set Variable    ${OUTPUT_DIR}/${file}
        ${ref_file}=     Set Variable    ${REFERENCE_DIR}/${file}
        File Should Exist    ${test_file}

        # MODIFIED: Replace the slow keyword with a single call to our fast one.
        # Robot Framework automatically converts the Python function name
        # 'compare_numeric_files_with_tolerance' into this keyword name.
        Compare Numeric Files With Tolerance    ${test_file}    ${ref_file}    ${TOLERANCE}
    END
