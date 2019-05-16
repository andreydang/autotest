*** Settings ***
Documentation     Task https://github.com/fedorovpv/testing
Library           ../test-task/TestTask.py

*** Variables ***
${OK}             202

*** Test Cases ***
Select Client With Balance
    [Documentation]    Выбор клиента с положительным балансом и не полным набором услуг ,если его нету то он будет создан
    Select Client With Balance

Get List Services Connected Client
    [Documentation]    Список подключенных услуг клиенту
    Get List Services Connected Client

Get Full List Services
    [Documentation]    Полный список услуг
    Req Get List Service

Get List Unconnected Services
    [Documentation]    Список неподключенных услуг клиенту
    Get List Unconnected Services

Connected Service To Client And Check
    [Documentation]    Подключение услуги клиенту и проверка корректности подключения
    Connected Service To Client And Check

*** Keywords ***
Get List Services Connected Client
    ${ID} =    Select Client With Balance
    Set Global Variable    ${ID}
    Req Post List Service    ${ID}

Get List Unconnected Services
    List Unconnected Service    ${ID}

Connected Service To Client And Check
    ${START_BALANCE} =    Client Balance    ${ID}
    Set Global Variable    ${START_BALANCE}
    ${SERVICE_ID} =    List Unconnected Service    ${ID}
    Set Global Variable    ${SERVICE_ID}
    Check Status
    Check Service In BD
    Check Connected Service With Api
    Check Correct Calculated Balance

Check Status
    ${STATUS} =    Req Post Add Service    ${ID}    ${SERVICE_ID}
    Should Be Equal As Integers    ${STATUS}    ${OK}

Check Service In BD
    ${SERVICE_ID_BD} =    Wait Until Keyword Succeeds    1 min    60 sec    Check Connected Service    ${ID}    ${SERVICE_ID}
    Should Be Equal As Integers    ${SERVICE_ID_BD}    ${SERVICE_ID}

Check Connected Service With Api
    ${RESULT_CHECK} =    Check Connected Service Api    ${ID}    ${SERVICE_ID}
    Should Be True    ${RESULT_CHECK}

Check Correct Calculated Balance
    ${END_BALANCE} =    Client Balance    ${ID}
    ${COST_SERVICE} =    Cost Service    ${SERVICE_ID}
    ${CALCULATED_BALANCE} =    Evaluate    ${START_BALANCE} - ${COST_SERVICE}
    Should Be Equal As Integers    ${END_BALANCE}    ${CALCULATED_BALANCE}
