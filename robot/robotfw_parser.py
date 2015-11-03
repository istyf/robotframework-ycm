#!/usr/bin/env python

import json
import logging
import os
import string
import subprocess


_logger = logging.getLogger( __name__ )


setting_table_names = ['Setting', 'Settings', 'Metadata']
variable_table_names = ['Variable', 'Variables']
test_case_table_names = ['Test Case', 'Test Cases']
keyword_table_names = ['Keyword', 'Keywords', 'User Keyword', 'User Keywords']

valid_table_names = setting_table_names + variable_table_names + test_case_table_names + keyword_table_names

setting_table_settings = ['Suite Setup', 'Suite Teardown', 'Test Setup', 'Test Teardown', 'Force Tags', 'Default Tags', 'Resource', 'Library']

library_names = ['Collections', 'DateTime', 'Dialogs', 'OperatingSystem', 'Process', 'Remote', 'Screenshot', 'String', 'Telnet', 'XML']

library_keywords = {
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
            ],
        'Dialogs' : [
            'Execute Manual Step', 'Get Selection From User', 'Get Value From User', 'Pause Execution'
            ],
        'OperatingSystem' : [
            ],
        'Process' : [
            ],
        'Remote' : [
            ],
        'Screenshot' : [
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
            ],
        'XML' : [
            ]
        }


class RobotFrameworkParser():
    
    def __init__(self, filename, contents, parent=None):
        self.filename_ = filename
        self.parent_ = parent

        self.defined_keywords = set()
        self.defined_test_cases = set()
        self.defined_variables = set()

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
        if len(setting) > 1:
            library_name = setting[1]
            _logger.info('Adding keywords from library {0}'.format(library_name))
            self.imported_libraries.add(library_name)


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

