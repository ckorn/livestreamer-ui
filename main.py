import sys
import os
import json

from PySide.QtGui import QApplication, QLabel, QPushButton, QLineEdit, QWidget, QTextEdit, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QKeySequence
from PySide.QtCore import Qt


from stream import Stream



    # FileNotFoundError is python3.3+ only
try:
    TryFileNotFound = FileNotFoundError

except NameError:
    TryFileNotFound = IOError



class LiveStreamer:

    def __init__( self ):

        url = QLineEdit()
        quality = QLineEdit()
        urlLabel = QLabel( 'Url' )
        qualityLabel = QLabel( 'Quality' )
        messages = QTextEdit()
        messagesLabel = QLabel( 'Messages' )
        links = QTableWidget( 0, 2 )
        linksLabel = QLabel( 'Links' )
        clearMessages = QPushButton( 'Clear Messages' )
        checkIfOnline = QPushButton( 'Check If Online' )
        addSelectedLink = QPushButton( 'Add Link' )
        removeSelectedLink = QPushButton( 'Remove Selected Link' )

        messages.setReadOnly( True )

        links.setHorizontalHeaderLabels( [ 'Url', 'Status' ] )
        links.horizontalHeader().setResizeMode( QHeaderView.Stretch )
        links.horizontalHeader().setResizeMode( 1, QHeaderView.Fixed )

            # set the events

        url.returnPressed.connect( self.select_stream_from_entry )
        quality.returnPressed.connect( self.select_stream_from_entry )
        links.itemDoubleClicked.connect( self.select_stream_from_link )
        clearMessages.clicked.connect( self.clear_messages )
        checkIfOnline.clicked.connect( self.check_if_online )
        addSelectedLink.clicked.connect( self.add_selected_link )
        removeSelectedLink.clicked.connect( self.remove_selected_link )

        #set shortcut
        checkIfOnline.setShortcut(QKeySequence(Qt.Key_F5))

            # set the layouts

        mainLayout = QGridLayout()

            # first row
        mainLayout.addWidget( urlLabel, 0, 0, 1, 1 )    # spans 1 column
        mainLayout.addWidget( qualityLabel, 0, 1, 1, 1 )# spans 1 column
        mainLayout.addWidget( linksLabel, 0, 2, 1, 3 )  # spans 3 columns

            # second row  (links widget occupies 2 rows and 2 columns)
        mainLayout.addWidget( url, 1, 0, 1, 1 )         # spans 1 column
        mainLayout.addWidget( quality, 1, 1, 1, 1 )     # spans 1 column
        mainLayout.addWidget( links, 1, 2, 2, 3 )   # spans 3 columns

            # third row (messages widget occupies 2 columns)
        mainLayout.addWidget( messages, 2, 0, 1, 2 )

            # fourth row
        mainLayout.addWidget( messagesLabel, 3, 0 )
        mainLayout.addWidget( clearMessages, 3, 1 )
        mainLayout.addWidget( checkIfOnline, 3, 2 )
        mainLayout.addWidget( addSelectedLink, 3, 3 )
        mainLayout.addWidget( removeSelectedLink, 3, 4 )


        window = QWidget()

        window.setLayout( mainLayout )
        window.setWindowTitle( 'Live Streamer' )
        window.resize( 700, 350 )
        window.show()

        self.url_ui = url
        self.quality_ui = quality
        self.messages_ui = messages
        self.links_ui = links
        self.window_ui = window

        self.links = set()

        self.data_file = os.path.join(os.path.expanduser("~"), ".config", "livestreamer-ui", "data.txt")
        folder=os.path.dirname(self.data_file)
        if not os.path.exists(folder):
                os.makedirs(folder)

    def get_complete_url(self):
        url = self.url_ui.text()

        if url:
            qual = self.quality_ui.text()
            if qual:
                url += " %s"%(qual)
        return url

    def select_stream_from_entry( self ):

        """
            Gets the values from the ui elements, and executes the program in json mode, to determine if the values are valid
        """
        url = self.get_complete_url()
        split_url = url.split()

        self.messages_ui.append( 'Trying to open stream: {}'.format( url ) )

        stream = Stream( split_url )

        stream.start( self.messages_ui )



    def select_stream_from_link( self, tableWidgetItem ):

        row = tableWidgetItem.row()

        urlItem = self.links_ui.item( row, 0 )  # the url is in the first column

        url = urlItem.text()

        split_url = url.split()

        self.messages_ui.append( 'Trying to open stream: {}'.format( url ) )


        stream = Stream( split_url )

        stream.start( self.messages_ui )



    def clear_messages( self ):

        self.messages_ui.setText( '' )


    def add_link( self, url ):

        """
            Adds a link to the link widget.

            Only adds if its not already present.
        """

        if url not in self.links:

            self.links.add( url )


            rowCounts = self.links_ui.rowCount()
            nextRow = rowCounts + 1
            nextPosition = rowCounts    # row count is the length, but position is zero-based

            self.links_ui.setRowCount( nextRow )

            urlEntry = QTableWidgetItem( url )
            statusEntry = QTableWidgetItem( '' )

            statusEntry.setTextAlignment( Qt.AlignCenter )

            urlEntry.setFlags( urlEntry.flags() & ~Qt.ItemIsEditable ) # not editable
            statusEntry.setFlags( statusEntry.flags() & ~Qt.ItemIsEditable ) # not editable

            self.links_ui.setItem( nextPosition, 0, urlEntry )
            self.links_ui.setItem( nextPosition, 1, statusEntry )


                # check if online
            stream = Stream( url.split() )

            stream.is_online( statusEntry )



    def add_selected_link( self ):

        url = self.get_complete_url()

        if url:

            self.add_link( url )


    def remove_selected_link( self ):

        selectedItem = self.links_ui.currentItem()

        if selectedItem:

            self.links.remove( selectedItem.text() )

            currentRow = self.links_ui.currentRow()
            self.links_ui.removeRow( currentRow )



    def check_if_online( self ):

        """
            Check if any of the streams saved is online
        """

        for row in range( self.links_ui.rowCount() ):

            urlItem = self.links_ui.item( row, 0 )
            statusItem = self.links_ui.item( row, 1 )

            url = urlItem.text()

            splitUrl = url.split()

            stream = Stream( splitUrl )

            stream.is_online( statusItem )





    def save( self ):

        """
            Save any data to a file (the links/etc)
        """

            # json doesn't have sets, so convert to a list
        linksList = list( self.links )

        saveJsonText = json.dumps( linksList )

        with open( self.data_file, 'w', encoding= 'utf-8' ) as f:
            f.write( saveJsonText )


    def load( self ):

        """
            Load any saved data
        """

        try:
            file = open( self.data_file, 'r', encoding= 'utf-8' )

        except TryFileNotFound:
            return


        linksList = json.loads( file.read() )

        file.close()


        for link in linksList:
            self.add_link( link )


        self.check_if_online()



if __name__ == '__main__':

    app = QApplication( sys.argv )

    streamer = LiveStreamer()

    streamer.load()

    app.aboutToQuit.connect( streamer.save )

    app.exec_()



