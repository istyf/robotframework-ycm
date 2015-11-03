#!/usr/bin/env python

import json
import logging
import os
import subprocess

from ycmd import responses
from ycmd import utils
from ycmd.completers.completer import Completer

from robotfw_parser import RobotFrameworkParser

ROBOTFW_FILETYPES = set( [ 'robot' ] )
COMPLETION_ERROR_MESSAGE = 'There was a completion error.'
PARSE_ERROR_MESSAGE = 'There was a parse error.'
NO_COMPLETIONS_MESSAGE = 'RF parser produced an empty JSON response.'
ROBOTFW_PANIC_MESSAGE = ( 'RF parser panicked trying to find completions, ' +
                          'you likely have a syntax error.' )

_logger = logging.getLogger( __name__ )


class RobotFrameworkCompleter( Completer ):

    subcommands = {
        'StartServer': ( lambda self, request_data: self._StartServer() ),
        'StopServer': ( lambda self, request_data: self._StopServer() ),
    }


    def __init__( self, user_options ):
        super( RobotFrameworkCompleter, self ).__init__( user_options )
        self._popener = utils.SafePopen # Overridden in test.
        self._parser = None

        _logger.info( 'Enabling robot framework completion' )


    def SupportedFiletypes( self ):
        return ROBOTFW_FILETYPES

    def ShouldUseNowInner( self, request_data ):
        filename = request_data[ 'filepath' ]
        contents = utils.ToUtf8IfNeeded(request_data[ 'file_data' ][ filename ][ 'contents' ])
        lines = contents.splitlines()

        line_num = request_data['line_num'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            try:
                column_num = request_data['column_num'] - 1
                resultdata = self._parser.candidates(line, line_num, column_num)

                if len(resultdata) == 2 and len(resultdata[1]) > 0:
                    return True

            except ValueError:
                pass

        return False


    def ComputeCandidatesInner( self, request_data ):
        filename = request_data[ 'filepath' ]
        contents = utils.ToUtf8IfNeeded(request_data[ 'file_data' ][ filename ][ 'contents' ])
        lines = contents.splitlines()

        line_num = request_data['line_num'] - 1

        if line_num < len(lines):
            line = lines[line_num]

            try:
                column_num = request_data['column_num'] - 1
                resultdata = self._parser.candidates(line, line_num, column_num)

                if len(resultdata) != 2:
                    _logger.error( NO_COMPLETIONS_MESSAGE )
                    raise RuntimeError( NO_COMPLETIONS_MESSAGE )

                return [ _ConvertCompletionData( x ) for x in resultdata[1] ]

            except ValueError:
                _logger.error( PARSE_ERROR_MESSAGE )
                raise RuntimeError( PARSE_ERROR_MESSAGE )

        return []


    def DefinedSubcommands( self ):
        return RobotFrameworkCompleter.subcommands.keys()


    def OnFileReadyToParse( self, request_data ):
        _logger.info( "file ready {0}".format(str(request_data)))

        filename = request_data[ 'filepath' ]
        contents = utils.ToUtf8IfNeeded(request_data[ 'file_data' ][ filename ][ 'contents' ])

        self._parser = RobotFrameworkParser(filename, contents)
        self._StartServer()


    def OnUserCommand( self, arguments, request_data ):
        if not arguments:
            raise ValueError( self.UserCommandsHelpMessage() )

        command = arguments[ 0 ]
        if command in RobotFrameworkCompleter.subcommands:
            command_lamba = RobotFrameworkCompleter.subcommands[ command ]
            return command_lamba( self, request_data )
        else:
            raise ValueError( self.UserCommandsHelpMessage() )


    def Shutdown( self ):
        self._StopServer()


    def _StartServer( self ):
        """ Start the RF server if we have one """
        pass


    def _StopServer( self ):
        """ Stop the RF server if we have one """
        pass


# Compute the byte offset in the file given the line and column.
# Code borrowed from the gocode completer
def _ComputeOffset( contents, line, col ):
    curline = 1
    curcol = 1

    for i, byte in enumerate( contents ):
        if curline == line and curcol == col:
            return i
        curcol += 1
        if byte == '\n':
            curline += 1
            curcol = 1

    _logger.error( 'RobotFrameworkCompleter - could not compute byte offset ' +
                   'corresponding to L%i C%i', line, col )
    return -1


def _ConvertCompletionData( completion_data ):
    return responses.BuildCompletionData(
        insertion_text = completion_data[ 'name' ],
        menu_text = completion_data[ 'name' ],
        extra_menu_info = completion_data[ 'type' ],
        kind = completion_data[ 'class' ],
        detailed_info = ' '.join( [
            completion_data[ 'name' ],
            completion_data[ 'type' ],
            completion_data[ 'class' ] ] ) )

