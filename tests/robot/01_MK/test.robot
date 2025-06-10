*** Settings ***
Library           OperatingSystem
Library           Process
Library           Collections

*** Variables ***
${SCRIPT}         -m
${MODULE}         lukefi.metsi.app.metsi
${INPUT_JSON}     ${CURDIR}/in/demo.json
${OUTPUT_DIR}     ${CURDIR}/out/test
${CONTROL_SCRIPT}  ${CURDIR}/in/demo_control_sim2.py
${REFERENCE_DIR}  ${CURDIR}/out/ref

*** Test Cases ***
Run Simulation And Compare Output Files
    [Tags]    simulation

    # Clean previous outputs
    Remove Directory  ${OUTPUT_DIR}  recursive=True
    Create Directory  ${OUTPUT_DIR}

    # Run the simulation
    ${result}=    Run Process    python    ${SCRIPT}    ${MODULE}    ${INPUT_JSON}    ${OUTPUT_DIR}    ${CONTROL_SCRIPT}    shell=True    stdout=YES    stderr=YES
    Log    STDOUT:\n${result.stdout}
    Log    STDERR:\n${result.stderr}
    Should Be Equal As Integers    ${result.rc}    0

    # Verify all expected output files exist and match reference files
    ${files}=    List Directory  ${REFERENCE_DIR}
	FOR    ${file}    IN    @{files}
		${test_file}=    Set Variable    ${OUTPUT_DIR}/${file}
		${ref_file}=     Set Variable    ${REFERENCE_DIR}/${file}
		File Should Exist    ${test_file}
		Files Should Be Equal    ${test_file}    ${ref_file}
	END

*** Keywords ***
Files Should Be Equal
    [Arguments]    ${file1}    ${file2}
    ${content1}=   Get File    ${file1}
    ${content2}=   Get File    ${file2}
    Should Be Equal    ${content1}    ${content2}