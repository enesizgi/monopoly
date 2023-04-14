**Project Selection:** An Online Monopoly Game Platform

**Team Members:**
* Boran Özüm - 2380814
* Muhammed Enes İzgi - 2310142

**Project Description**

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