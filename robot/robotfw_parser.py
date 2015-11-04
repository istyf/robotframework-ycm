#!/usr/bin/env python

import json
import logging
import os
import string
import subprocess


_logger = logging.getLogger(__name__)


setting_table_names = ['Setting', 'Settings', 'Metadata']
variable_table_names = ['Variable', 'Variables']
test_case_table_names = ['Test Case', 'Test Cases']
keyword_table_names = ['Keyword', 'Keywords', 'User Keyword', 'User Keywords']

valid_table_names = setting_table_names + variable_table_names + test_case_table_names + keyword_table_names

setting_table_settings = ['Suite Setup', 'Suite Teardown', 'Test Setup', 'Test Teardown', 'Force Tags', 'Default Tags', 'Resource', 'Library']

library_names = ['ArchiveLibrary', 'Collections', 'DateTime', 'Dialogs', 'OperatingSystem', 'Process', 'Remote', 'Screenshot', 'Selenium2Library', 'SSHLibrary', 'String', 'Telnet', 'XML']

library_keywords = {
        'ArchiveLibrary' : [
            'Archive Should Contain File', 'Extract Tar File', 'Extract Zip File'
            ],
        'BuiltIn' : [
            'Call Method', 'Catenate', 'Comment', 'Continue For Loop', 'Continue For Loop If', 'Convert To Binary',
            'Convert To Boolean', 'Convert To Bytes', 'Convert To Hex', 'Convert To Integer', 'Convert To Number',
            'Convert To Octal', 'Convert To String', 'Create Dictionary', 'Create List', 'Evaluate', 'Exit For Loop',
            'Exit For Loop If', 'Fail', 'Fatal Error', 'Get Count', 'Get Length', 'Get Library Instance', 'Get Time',
            'Get Variable Value', 'Get Variables', 'Import Library', 'Import Resource', 'Import Variables',
            'Keyword Should Exist', 'Length Should Be', 'Log', 'Log Many', 'Log To Console', 'Log Variables',
            'No Operation', 'Pass Execution', 'Pass Execution If', 'Regexp Escape', 'Reload Library', 'Remove Tags',
            'Repeat Keyword', 'Replace Variables', 'Return From Keyword', 'Return From Keyword If', 'Run Keyword',
            'Run Keyword And Continue On Failure', 'Run Keyword And Expect Error', 'Run Keyword And Ignore Error',
            'Run Keyword And Return', 'Run Keyword And Return If', 'Run Keyword And Return Status', 'Run Keyword If',
            'Run Keyword If All Critical Tests Passed', 'Run Keyword If All Tests Passed',
            'Run Keyword If Any Critical Tests Failed', 'Run Keyword If Any Tests Failed',
            'Run Keyword If Test Failed', 'Run Keyword If Test Passed', 'Run Keyword If Timeout Occurred',
            'Run Keyword Unless', 'Run Keywords', 'Set Global Variable', 'Set Library Search Order', 'Set Log Level',
            'Set Suite Documentation', 'Set Suite Metadata', 'Set Suite Variable', 'Set Tags',
            'Set Test Documentation', 'Set Test Message', 'Set Test Variable', 'Set Variable', 'Set Variable If',
            'Should Be Empty', 'Should Be Equal', 'Should Be Equal As Integers', 'Should Be Equal As Numbers',
            'Should Be Equal As Strings', 'Should Be True', 'Should Contain', 'Should Contain X Times',
            'Should End With', 'Should Match', 'Should Match Regexp', 'Should Not Be Empty', 'Should Not Be Equal',
            'Should Not Be Equal As Integers', 'Should Not Be Equal As Numbers', 'Should Not Be Equal As Strings',
            'Should Not Be True', 'Should Not Contain', 'Should Not End With', 'Should Not Match',
            'Should Not Match Regexp', 'Should Not Start With', 'Should Start With', 'Sleep', 'Variable Should Exist',
            'Variable Should Not Exist', 'Wait Until Keyword Succeeds'
            ],
        'Collections' : [
            'Append To List', 'Combine Lists', 'Convert To Dictionary', 'Convert To List', 'Copy Dictionary',
            'Copy List', 'Count Values In List', 'Dictionaries Should Be Equal', 'Dictionary Should Contain Item',
            'Dictionary Should Contain Key', 'Dictionary Should Contain Sub Dictionary',
            'Dictionary Should Contain Value', 'Dictionary Should Not Contain Key',
            'Dictionary Should Not Contain Value', 'Get Dictionary Items', 'Get Dictionary Keys',
            'Get Dictionary Values', 'Get From Dictionary', 'Get From List', 'Get Index From List', 'Get Match Count',
            'Get Matches', 'Get Slice From List', 'Insert Into List', 'Keep In Dictionary',
            'List Should Contain Sub List', 'List Should Contain Value', 'List Should Not Contain Duplicates',
            'List Should Not Contain Value', 'Lists Should Be Equal', 'Log Dictionary', 'Log List',
            'Pop From Dictionary', 'Remove Duplicates', 'Remove From Dictionary', 'Remove From List',
            'Remove Values From List', 'Reverse List', 'Set List Value', 'Set To Dictionary', 'Should Contain Match',
            'Should Not Contain Match', 'Sort List'
            ],
        'DateTime' : [
            'Add Time To Date', 'Add Time To Time', 'Convert Date', 'Convert Time', 'Get Current Date',
            'Subtract Date From Date', 'Subtract Time From Date', 'Subtract Time From Time'
            ],
        'Dialogs' : [
            'Execute Manual Step', 'Get Selection From User', 'Get Value From User', 'Pause Execution'
            ],
        'OperatingSystem' : [
            'Append To Environment Variable', 'Append To File', 'Copy Directory', 'Copy File', 'Copy Files',
            'Count Directories In Directory', 'Count Files In Directory', 'Count Items In Directory',
            'Create Binary File', 'Create Directory', 'Create File', 'Directory Should Be Empty',
            'Directory Should Exist', 'Directory Should Not Be Empty', 'Directory Should Not Exist', 'Empty Directory',
            'Environment Variable Should Be Set', 'Environment Variable Should Not Be Set', 'File Should Be Empty',
            'File Should Exist', 'File Should Not Be Empty', 'File Should Not Exist', 'Get Binary File',
            'Get Environment Variable', 'Get Environment Variables', 'Get File', 'Get File Size', 'Get Modified Time',
            'Grep File', 'Join Path', 'Join Paths', 'List Directories In Directory', 'List Directory',
            'List Files In Directory', 'Log Environment Variables', 'Log File', 'Move Directory', 'Move File',
            'Move Files', 'Normalize Path', 'Read Process Output', 'Remove Directory', 'Remove Environment Variable',
            'Remove File', 'Remove Files', 'Run', 'Run And Return Rc', 'Run And Return Rc And Output',
            'Set Environment Variable', 'Set Modified Time', 'Should Exist', 'Should Not Exist', 'Split Extension',
            'Split Path', 'Start Process', 'Stop All Processes', 'Stop Process', 'Switch Process', 'Touch',
            'Wait Until Created', 'Wait Until Removed'
            ],
        'Process' : [
            'Get Process Id', 'Get Process Object', 'Get Process Result', 'Is Process Running', 'Join Command Line',
            'Process Should Be Running', 'Process Should Be Stopped', 'Run Process', 'Send Signal To Process',
            'Split Command Line', 'Start Process', 'Switch Process', 'Terminate All Processes', 'Terminate Process',
            'Wait For Process'
            ],
        'Screenshot' : [
            'Set Screenshot Directory', 'Take Screenshot', 'Take Screenshot Without Embedding'
            ],
        'Selenium2Library' : [
            'Add Cookie', 'Add Location Strategy', 'Alert Should Be Present', 'Assign Id To Element',
            'Capture Page Screenshot', 'Checkbox Should Be Selected', 'Checkbox Should Not Be Selected',
            'Choose Cancel On Next Confirmation', 'Choose File', 'Choose Ok On Next Confirmation', 'Clear Element Text',
            'Click Button', 'Click Element', 'Click Element At Coordinates', 'Click Image', 'Click Link',
            'Close All Browsers', 'Close Browser', 'Close Window', 'Confirm Action', 'Create Webdriver',
            'Current Frame Contains', 'Current Frame Should Not Contain', 'Delete All Cookies', 'Delete Cookie',
            'Dismiss Alert', 'Double Click Element', 'Drag And Drop', 'Drag And Drop By Offset',
            'Element Should Be Disabled', 'Element Should Be Enabled', 'Element Should Be Visible',
            'Element Should Contain', 'Element Should Not Be Visible', 'Element Should Not Contain',
            'Element Text Should Be', 'Execute Async Javascript', 'Execute Javascript', 'Focus', 'Frame Should Contain',
            'Get Alert Message', 'Get All Links', 'Get Cookie Value', 'Get Cookies', 'Get Element Attribute',
            'Get Horizontal Position', 'Get List Items', 'Get Location', 'Get Matching Xpath Count',
            'Get Selected List Label', 'Get Selected List Labels', 'Get Selected List Value',
            'Get Selected List Values', 'Get Selenium Implicit Wait', 'Get Selenium Speed', 'Get Selenium Timeout',
            'Get Source', 'Get Table Cell', 'Get Text', 'Get Title', 'Get Value', 'Get Vertical Position',
            'Get Webelement', 'Get Webelements', 'Get Window Identifiers', 'Get Window Names', 'Get Window Position',
            'Get Window Size', 'Get Window Titles', 'Go Back', 'Go To', 'Input Password', 'Input Text',
            'Input Text Into Prompt', 'List Selection Should Be', 'List Should Have No Selections', 'List Windows',
            'Location Should Be', 'Location Should Contain', 'Locator Should Match X Times', 'Log Location',
            'Log Source', 'Log Title', 'Maximize Browser Window', 'Mouse Down', 'Mouse Down On Image',
            'Mouse Down On Link', 'Mouse Out', 'Mouse Over', 'Mouse Up', 'Open Browser', 'Open Context Menu',
            'Page Should Contain', 'Page Should Contain Button', 'Page Should Contain Checkbox',
            'Page Should Contain Element', 'Page Should Contain Image', 'Page Should Contain Link',
            'Page Should Contain List', 'Page Should Contain Radio Button', 'Page Should Contain Textfield',
            'Page Should Not Contain', 'Page Should Not Contain Button', 'Page Should Not Contain Checkbox',
            'Page Should Not Contain Element', 'Page Should Not Contain Image', 'Page Should Not Contain Link',
            'Page Should Not Contain List', 'Page Should Not Contain Radio Button', 'Page Should Not Contain Textfield',
            'Press Key', 'Radio Button Should Be Set To', 'Radio Button Should Not Be Selected',
            'Register Keyword To Run On Failure', 'Reload Page', 'Remove Location Strategy', 'Select All From List',
            'Select Checkbox', 'Select Frame', 'Select From List', 'Select From List By Index',
            'Select From List By Label', 'Select From List By Value', 'Select Radio Button', 'Select Window',
            'Set Browser Implicit Wait', 'Set Screenshot Directory', 'Set Selenium Implicit Wait', 'Set Selenium Speed',
            'Set Selenium Timeout', 'Set Window Position', 'Set Window Size', 'Simulate', 'Submit Form',
            'Switch Browser', 'Table Cell Should Contain', 'Table Column Should Contain', 'Table Footer Should Contain',
            'Table Header Should Contain', 'Table Row Should Contain', 'Table Should Contain',
            'Textarea Should Contain', 'Textarea Value Should Be', 'Textfield Should Contain',
            'Textfield Value Should Be', 'Title Should Be', 'Unselect Checkbox', 'Unselect Frame', 'Unselect From List',
            'Unselect From List By Index', 'Unselect From List By Label', 'Unselect From List By Value',
            'Wait For Condition', 'Wait Until Element Contains', 'Wait Until Element Does Not Contain',
            'Wait Until Element Is Enabled', 'Wait Until Element Is Not Visible', 'Wait Until Element Is Visible',
            'Wait Until Page Contains', 'Wait Until Page Contains Element', 'Wait Until Page Does Not Contain',
            'Wait Until Page Does Not Contain Element', 'Xpath Should Match X Times'
            ],
        'SSHLibrary' : [
            'Close All Connections', 'Close Connection', 'Directory Should Exist', 'Directory Should Not Exist',
            'Enable Ssh Logging', 'Execute Command', 'File Should Exist', 'File Should Not Exist', 'Get Connection',
            'Get Connections', 'Get Directory', 'Get File', 'List Directories In Directory', 'List Directory',
            'List Files In Directory', 'Login', 'Login With Public Key', 'Open Connection', 'Put Directory', 'Put File',
            'Read', 'Read Command Output', 'Read Until', 'Read Until Prompt', 'Read Until Regexp',
            'Set Client Configuration', 'Set Default Configuration', 'Start Command', 'Switch Connection', 'Write',
            'Write Bare', 'Write Until Expected Output'
            ],
        'String' : [
            'Convert To Lowercase', 'Convert To Uppercase', 'Decode Bytes To String', 'Encode String To Bytes',
            'Fetch From Left', 'Fetch From Right', 'Generate Random String', 'Get Line', 'Get Line Count',
            'Get Lines Containing String', 'Get Lines Matching Pattern', 'Get Lines Matching Regexp',
            'Get Regexp Matches', 'Get Substring', 'Remove String', 'Remove String Using Regexp', 'Replace String',
            'Replace String Using Regexp', 'Should Be Byte String', 'Should Be Lowercase', 'Should Be String',
            'Should Be Titlecase', 'Should Be Unicode String', 'Should Be Uppercase', 'Should Not be String',
            'Split String', 'Split String From Right', 'Split String To Characters', 'Split To Lines'
            ],
        'Telnet' : [
            'Close All Connections', 'Close Connection', 'Execute Command', 'Login', 'Open Connection', 'Read',
            'Read Until', 'Read Until Prompt', 'Read Until Regexp', 'Set Default Log Level', 'Set Encoding',
            'Set Newline', 'Set Prompt', 'Set Telnetlib Log Level', 'Set Timeout', 'Switch Connection', 'Write',
            'Write Bare', 'Write Control Character', 'Write Until Expected Output'
            ],
        'XML' : [
            'Add Element', 'Clear Element', 'Copy Element', 'Element Attribute Should Be',
            'Element Attribute Should Match', 'Element Should Exist', 'Element Should Not Exist',
            'Element Should Not Have Attribute', 'Element Text Should Be', 'Element Text Should Match',
            'Element To String', 'Elements Should Be Equal', 'Elements Should Match', 'Evaluate Xpath',
            'Get Child Elements', 'Get Element', 'Get Element Attribute', 'Get Element Attributes', 'Get Element Count',
            'Get Element Text', 'Get Elements', 'Get Elements Texts', 'Log Element', 'Parse Xml', 'Remove Element',
            'Remove Element Attribute', 'Remove Element Attributes', 'Remove Elements', 'Remove Elements Attribute',
            'Remove Elements Attributes', 'Save Xml', 'Set Element Attribute', 'Set Element Tag', 'Set Element Text',
            'Set Elements Attribute', 'Set Elements Tag', 'Set Elements Text'
            ]
        }


class RobotFrameworkParser():
    
    def __init__(self, filename, contents, parent=None):
        self.filename_ = filename
        self.parent_ = parent

        self.defined_keywords = set()
        self.defined_test_cases = set()
        self.defined_variables = set()

        self.defined_library_aliases = {}

        self.imported_resources = set()
        self.imported_libraries = set()

        self.defined_variables.add('${EMPTY}')
        self.defined_variables.add('${True}')
        self.defined_variables.add('${False}')

        self.imported_libraries.add('BuiltIn')

        self._parse(contents)


    def has_imported_resource(self, path):
        if path in self.imported_resources:
            return True

        if self.parent_:
            return self.parent_.has_imported_resource(path)

        return False


    def _locate_resource(self, resource):
        resource_dirs = resource.split(os.sep)
        while resource_dirs and resource_dirs[0] == '..':
            resource_dirs = resource_dirs[1:]

        parent_dirs = self.filename_.split(os.sep)[0:-1]
        resource_path = str(os.sep).join(resource_dirs)

        while parent_dirs:
            path = str(os.sep).join(parent_dirs) + os.sep + resource_path
            if os.path.isfile(path):
                return path

            parent_dirs = parent_dirs[0:-1]

        return None


    def _import_resource(self, resource):
        _logger.info('Importing resource {0} ...'.format(resource))
        path = self._locate_resource(resource)
        if path:
            _logger.info('    ... located file at {0}'.format(path))

            if not self.has_imported_resource(path):
                try:
                    contents = ''
                    with open(path, 'r') as f:
                        contents = f.read()

                    self.imported_resources.add(path)
                    parser = RobotFrameworkParser(path, contents, self)

                    for tc in parser.defined_test_cases:
                        self.defined_test_cases.add(tc)
                    for kw in parser.defined_keywords:
                        self.defined_keywords.add(kw)
                    for v in parser.defined_variables:
                        self.defined_variables.add(v)

                    for alias, library_name in parser.defined_library_aliases.iteritems():
                        self.defined_library_aliases[alias] = library_name

                    for l in parser.imported_libraries:
                        self.imported_libraries.add(l)
                    for r in parser.imported_resources:
                        self.imported_resources.add(r)
                except Exception as e:
                    _logger.error('An exception was thrown when attempting to parse {0}: {1}'.format(path, e.message))

            else:
                _logger.info('    ... already imported. Skipping.')


    def _parse(self, contents):
        lines_raw = contents.splitlines()
        filtered_lines = []

        for line in lines_raw:
            if line:
                parts = line.split('|')
                if len(parts) > 2:
                    parts = parts[1:-1]
                    for p in range(0, len(parts)):
                        parts[p] = parts[p].strip()
                    filtered_lines.append(parts)

        (table_name, filtered_lines) = self._skip_to_next_table(filtered_lines)

        while filtered_lines:
            if table_name == "Settings":
                filtered_lines = self._parse_settings(filtered_lines)
            elif table_name == "Variables":
                filtered_lines = self._parse_variables(filtered_lines)
            elif table_name == "Test Cases":
                filtered_lines = self._parse_test_cases(filtered_lines)
            elif table_name == "Keywords":
                filtered_lines = self._parse_keywords(filtered_lines)

            if filtered_lines:
                (table_name, filtered_lines) = self._skip_to_next_table(filtered_lines)


    def _parse_keywords(self, lines):
        for l in range(0, len(lines)):
            first_cell_content = str(lines[l][0])

            if first_cell_content.startswith('*'):
                return lines[l:]

            if first_cell_content:
                _logger.info('Found keyword {0}'.format(first_cell_content))
                self.defined_keywords.add(first_cell_content)

        return []


    def _parse_library_setting(self, setting):
        setting_length = len(setting)

        if setting_length > 1:
            library_name = setting[1]

            _logger.info('Adding keywords from library {0}'.format(library_name))
            self.imported_libraries.add(library_name)

            if setting_length >= 4:
                if str(setting[setting_length - 2]).upper() == "WITH NAME":
                    alias = setting[setting_length - 1]

                    _logger.info('Adding alias {0} for library {1}'.format(alias, library_name))
                    self.defined_library_aliases[alias] = library_name


    def _parse_settings(self, lines):
        for l in range(0, len(lines)):
            first_cell_content = str(lines[l][0])

            if first_cell_content.startswith('*'):
                return lines[l:]

            if first_cell_content == 'Resource':
                if len(lines[l]) > 1:
                    self._import_resource(lines[l][1])
            elif first_cell_content == 'Library':
                self._parse_library_setting(lines[l])

        return []


    def _parse_test_cases(self, lines):
        for l in range(0, len(lines)):
            first_cell_content = str(lines[l][0])

            if first_cell_content.startswith('*'):
                return lines[l:]

            if first_cell_content:
                _logger.info('Found test case {0}'.format(first_cell_content))
                self.defined_test_cases.add(first_cell_content)

        return []


    def _parse_variables(self, lines):
        for l in range(0, len(lines)):
            first_cell_content = str(lines[l][0])

            if first_cell_content.startswith('*'):
                return lines[l:]

            if first_cell_content:
                _logger.info('Adding variable {0}'.format(first_cell_content))
                self.defined_variables.add(first_cell_content)


    def _skip_to_next_table(self, lines):
        line_count = len(lines)

        if line_count > 1:
            for l in range(0, line_count-1):
                first_cell_content = str(lines[l][0])

                if first_cell_content.startswith('*'):
                    first_cell_content = first_cell_content.strip('* ')

                    if first_cell_content in setting_table_names:
                        return ('Settings', lines[l+1:])
                    elif first_cell_content in variable_table_names:
                        return ('Variables', lines[l+1:])
                    elif first_cell_content in test_case_table_names:
                        return ('Test Cases', lines[l+1:])
                    elif first_cell_content in keyword_table_names:
                        return ('Keywords', lines[l+1:])

        return (None, [])


    def _word_before_index(self, line, idx):
        if idx > 0:
            start_of_word = idx - 1

            while str(line[start_of_word]).isalnum():
                if start_of_word == 0:
                    return line[0:idx]
                else:
                    start_of_word = start_of_word - 1

            if start_of_word < (idx - 1):
                return line[start_of_word + 1:idx]

        return None


    def _context(self, line, line_num, idx):
        table_column = line.count('|', 0, idx)

        if table_column == 0:
            return {'table' : None}

        return {'table':'unknown', 'col':table_column-1, 'columns':line.split('|')[1:]}


    def candidates( self, line, line_num, idx ):

        available_candidates = []
        no_candidates = [{},[]]

        line_length = len(line)

        if idx > 0:
            _logger.info('getting completions at {0}/{1} for line {2}'.format(idx, line_length, line))

            context = self._context(line, line_num, idx)

            if line[idx-1] == '|' or context['table'] == None:
                return no_candidates

            if line[idx-1] == '.':
                library_alias = self._word_before_index(line, idx - 1)

                if library_alias in self.defined_library_aliases:
                    library_name = self.defined_library_aliases[library_alias]

                    if library_name in library_keywords:
                        keywords = library_keywords[library_name]

                        if len(keywords) > 0:
                            for kw in keywords:
                                available_candidates.append({'name':kw, 'type':'K', 'class':library_name})

                            return [{}, available_candidates]


            table_column = context['col']
            columns = context['columns']

            # TODO: This should check that we are in the settings table ...
            if table_column == 0:
                for setting in setting_table_settings:
                    available_candidates.append({'name':setting, 'type':'S', 'class':'Setting'})


            if table_column == 1:
                if columns[0].strip() == 'Library':
                    # TODO: Check that we are in a settings table
                    for lib in library_names:
                        if lib not in self.imported_libraries:
                            available_candidates.append({'name':lib, 'type':'L', 'class':'Library'})
                else:
                    for alias, _ in self.defined_library_aliases.iteritems():
                        available_candidates.append({'name':alias, 'type':'L', 'class':'Library'})

                    for lib in self.imported_libraries:
                        if lib in library_keywords:
                            keywords = library_keywords[lib]
                            for kw in keywords:
                                available_candidates.append({'name':kw, 'type':'K', 'class':lib})

                    for kw in self.defined_keywords:
                        available_candidates.append({'name':kw, 'type':'k', 'class':'user defined'})


            if table_column > 1:
                for variable in self.defined_variables:
                    available_candidates.append({'name':variable, 'type':'V', 'class':'Variable'})

        
        return [{}, available_candidates]

