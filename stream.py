import json

from PySide.QtCore import QProcess, Qt
from PySide.QtGui import QColor, QBrush


class Stream:

    ALL_STREAMS = []

    def __init__( self, arguments ):

        self.arguments = arguments


    def start( self, messageElement ):

        Stream.clear_streams()

        process = QProcess()

        self.process = process
        self.messageElement = messageElement

        process.setProcessChannelMode( QProcess.MergedChannels )
        process.start( 'livestreamer', self.arguments )
        process.readyReadStandardOutput.connect( self.show_messages )

        Stream.ALL_STREAMS.append( self )



    def is_online( self, tableWidgetItem ):

        Stream.clear_streams()

        process = QProcess()

        self.process = process
        self.table_widget_item = tableWidgetItem

        arguments = [ '--json' ] + self.arguments

        process.setProcessChannelMode( QProcess.MergedChannels )
        process.start( 'livestreamer', arguments )
        process.readyReadStandardOutput.connect( self.is_online_callback )

        brush=QBrush(Qt.SolidPattern)
        color=QColor(255,255,255) #white
        brush.setColor(color)
        tableWidgetItem.setBackground( brush )
        tableWidgetItem.setText( 'Checking..' )

        Stream.ALL_STREAMS.append( self )


    def is_online_callback( self ):

        outputBytes = self.process.readAll().data()

        outputUnicode = outputBytes.decode( 'utf-8' )

        try:
            outputObject = json.loads( outputUnicode )

        except ValueError as errorMessage:
            print( errorMessage )
            return

        brush=QBrush(Qt.SolidPattern)
        if outputObject.get( 'error' ):
            color=QColor(255,0,0) #red
            onlineStatus = 'Off'
        else:
            color=QColor(0,255,0) #green
            onlineStatus = 'On'
        brush.setColor(color)


        itemWidget = self.table_widget_item

        itemWidget.setBackground( brush )
        itemWidget.setText( onlineStatus )


    def show_messages( self ):

        outputBytes = self.process.readAll().data()

        outputUnicode = outputBytes.decode( 'utf-8' )

        self.messageElement.append( outputUnicode )



    @staticmethod
    def clear_streams():

        """
            Remove the streams that have ended (process is not running anymore) from the list that contains all the stream objects
        """

        streams = []

        for stream in Stream.ALL_STREAMS:

            if stream.process.state() != QProcess.NotRunning:

                streams.append( stream )


        Stream.ALL_STREAMS = streams
