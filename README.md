**Project Selection:** An Online Monopoly Game Platform

**Team Members:**
* Boran Özüm - 2380814
* Muhammed Enes İzgi - 2310142

**Project Description**

**Phase 1**

We have created several classes to make it easier to code this project.

1. **Board Class:** This is our main class. It manages the game.
2. **Player Class:** This class represents the players in the game.
3. **Cell Class:** This class represents every cell in the board.
4. **Subclasses of Cell Class:** These classes represent the different types of cells in the game.
   * **ChanceCard Class:** This class represents the chance card cell. Player draws a chance card when they come here.
   * **GotoJail Class:** This class represents the gotojail cell. Player goes to jail when they come here.
   * **Jail Class:** This class represents the jail cell. Player stays in this cell when they are in jail.
   * **Lottery Class:** This class represents the lottery cell. Player gets the lottery fee when they come here.
   * **Property Class:** This class represents the property cell. Player can buy/upgrade/downgrade this cell when they come here.
   * **Start Class:** This class represents the start cell. Players start here. They get the start fee every time they pass this cell.
   * **Tax Class:** This class represents the tax cell. Player pays the tax fee when they come here.
   * **Teleport Class:** This class represents the teleport cell. Player can teleport to another cell by paying teleport fee when they come here.

**Phase 2**

We have included three new files for this phase to implement TCP communication between users
and board. These files are:

1. **client.py:** This class represents the client. It connects to the server and sends/receives messages to/from the server.
2. **app.py:** This class represents the server. It listens to the clients and sends/receives messages to/from the clients.
3. **TCPMessage.py:** This class represents the messages that are sent between the server and the clients.

**Phase 3**

We have created a Django project for this phase. We have created a new app called "monopoly" and we have moved our code to this app.
In addition to the default files for the Django project, we have created the following files:

1. **views.py:** This file contains the functions that are called when a user sends a request to the server.
2. **signals.py:** This file contains the functions that are called to handle extra work when a user logs in or logs out.
3. **db.sqlite3:** This file contains the database of the project.
4. **templates:** This folder contains the html files that are used to render the pages. These html files include:
     1. **base.html:** This file is the base html file. Other html files extend this file.
   2. **home.html:** This file is the home page of the project. It contains the list of available games.
   3. **board.html:** This file is the game page of the project. It contains the board and the form data.