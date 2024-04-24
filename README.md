# securedgroupfileservers
Final project for Applied Cryptography course.


YOU NEED TO GENERATE YOUR OWN CERTIFICATE FOR THE APP TO WORK.

use san.caf and run the line below for loopback valid certificate

	openssl req -x509 -nodes -days 730 -newkey rsa:2048 -keyout key.pem -out cert.pem -config san.cnf




The system is somewhat secure.
data.json servers as a centralized database.

The group server performs operations on users, tokens, and groups.

The file server handles uploading and downloading files.

Technically you could run it on a legit file server - but **I wouldn't recommend it**. The whole system is rather a fun project to learn about the implementation of security measurements during software development, not viable to run in production.

**Feel free to be inspired.**


############# GROUP SERVER INSTRUCTIONS ##############

    Step 1: Run the Group Server code either by pressing play or typing in the terminal the following command "python3 Group_Server.py"

    Step 2: Once the server is up and running, run the Client_Code in a new window by either pressing play or typing the following command in the terminal "python3 Client_Code.py" 

    Step 3: Once the client is connected to the server, press enter, then type the command "help" and press enter to show the different 
	    commands you can run while in the group server. Commands are in the following format COMMAND;var1;var2 etc.

############# FILE SERVER INSTRUCTIONS ###############

    Step 1: Run the File_Server code either by pressing play or typing in the terminal the following command "python3 File_Server.py"
    
    Step 2: Once the file server is up and running, run the File_Client in a new window by either pressing play or typing the following command in the 
	    terminal "python3 Client_Code.py"
     
    Step 3: Once the client is connected to the server, press enter, then type the command "help" and press enter to show the different 
	    commands you can run while in the file_server. Commands are in the following format COMMAND;var1;var2 etc.

     

	Make sure to change FILE_STORAGE_PATH = 'D:\\CryptoCode\\file_storage' (line11) in File_Operations.py to a path where you want your files uploaded.


############ APPENDIX #############

Make sure that File_Operations is in the same folder as File_Server.
Same for Json_Operations and Group_Server.
Both servers refer to data.json, make sure they're in the same directory with this file.
    If the code has trouble reading the data.json make sure you run your compiler as administrator.
