--
-- File generated with SQLiteStudio v3.2.1 on Sun Apr 21 16:54:07 2019
--
-- Text encoding used: System
--
-- Table: ChannelCategories
CREATE TABLE ChannelCategories (
    ID   INTEGER NOT NULL,
    Name TEXT    NOT NULL,
    PRIMARY KEY (ID)
);

-- Table: Channels
CREATE TABLE Channels (
    ID       INTEGER NOT NULL,
    Name     TEXT    NOT NULL,
    Type     TEXT    NOT NULL,
    Category INTEGER,
    PRIMARY KEY (ID),
    FOREIGN KEY (Category) REFERENCES ChannelCategories (ID) ON UPDATE CASCADE
);

-- Table: Credits
CREATE TABLE Credits (
    User    INTEGER NOT NULL,
    Credits INTEGER NOT NULL
                    DEFAULT 0,
    PRIMARY KEY (User),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE
);

-- Table: Dailies
CREATE TABLE Dailies (
    User      INTEGER NOT NULL,
    DailyUses INTEGER NOT NULL
                      DEFAULT 0,
    LastDaily INTEGER NOT NULL
                      DEFAULT 0,
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    PRIMARY KEY (User)
);

-- Table: FM
CREATE TABLE FM (
    User           INTEGER NOT NULL,
    LastFMUsername TEXT    NOT NULL,
    LastUpdated    INTEGER NOT NULL,
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    PRIMARY KEY (User)
);

-- Table: Golds
CREATE TABLE Golds (
    User INTEGER NOT NULL, TimeGiven INTEGER NOT NULL, GivenBy INTEGER REFERENCES Users (ID) ON UPDATE CASCADE NOT NULL, GoldID INTEGER PRIMARY KEY NOT NULL, FOREIGN KEY(User) REFERENCES Users (ID) ON UPDATE CASCADE);

-- Table: Levels
CREATE TABLE Levels (User INTEGER NOT NULL, Level INTEGER NOT NULL DEFAULT 0, Points INTEGER NOT NULL DEFAULT 0, MonthLevel INTEGER NOT NULL DEFAULT 0, MonthPoints INTEGER NOT NULL DEFAULT 0, NextPoint INTEGER DEFAULT (0), PRIMARY KEY (User), FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE);

-- Table: Mutes
CREATE TABLE Mutes (User INTEGER PRIMARY KEY REFERENCES Users (ID) ON UPDATE CASCADE NOT NULL, UnmuteTime INTEGER NOT NULL);

-- Table: OwnedRoles
CREATE TABLE OwnedRoles (
    User         INTEGER NOT NULL,
    Role         INTEGER NOT NULL,
    PurchaseDate INTEGER NOT NULL,
    PurchaseID   INTEGER NOT NULL,
    PRIMARY KEY (PurchaseID),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    FOREIGN KEY (Role) REFERENCES Roles (ID) ON UPDATE CASCADE
);

-- Table: Reminders
CREATE TABLE Reminders (User INTEGER REFERENCES Users (ID) ON UPDATE CASCADE NOT NULL, Reminder TEXT NOT NULL, Date INTEGER NOT NULL, RemindID INTEGER PRIMARY KEY  NOT NULL);

-- Table: Roles
CREATE TABLE Roles (
    Name     TEXT    NOT NULL,
    ID       INTEGER NOT NULL,
    Color    TEXT    NOT NULL,
    Priority INTEGER NOT NULL
                     UNIQUE,
    PRIMARY KEY (ID)
);

-- Table: Tags
CREATE TABLE Tags (TagName TEXT NOT NULL, User INTEGER NOT NULL, Content TEXT NOT NULL, LastUpdated INTEGER NOT NULL, FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE, PRIMARY KEY (TagName));

-- Table: Users
CREATE TABLE Users (
    ID          INTEGER NOT NULL,
    Name        TEXT    NOT NULL,
    JoinDate    INTEGER NOT NULL,
    CreatedDate INTEGER NOT NULL,
    PrimaryRole INTEGER NOT NULL,
    [Left]        TEXT    NOT NULL
                        DEFAULT 'F',
    FOREIGN KEY (PrimaryRole) REFERENCES Roles (ID) ON UPDATE CASCADE,
    PRIMARY KEY (ID)
);

-- Table: Warnings
CREATE TABLE Warnings (
    User     INTEGER NOT NULL,
    Reason   TEXT    NOT NULL,
    Date     INTEGER NOT NULL,
    WarnedBy INTEGER NOT NULL,
    WarnID   INTEGER NOT NULL,
    PRIMARY KEY (WarnID),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    FOREIGN KEY (WarnedBy)REFERENCES Users (ID) ON UPDATE CASCADE
);
