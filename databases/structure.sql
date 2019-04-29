CREATE TABLE ChannelCategories (
    ID   BIGINT NOT NULL,
    Name VARCHAR(30) NOT NULL,
    PRIMARY KEY (ID)
);

CREATE TABLE Channels (
    ID       BIGINT NOT NULL,
    Name     VARCHAR(40)    NOT NULL,
    Type     VARCHAR(8)    NOT NULL,
    Category BIGINT,
    PRIMARY KEY (ID),
    FOREIGN KEY (Category) REFERENCES ChannelCategories (ID) ON UPDATE CASCADE
);

CREATE TABLE Roles (
    Name     VARCHAR(50)    NOT NULL,
    ID       BIGINT NOT NULL,
    Color    VARCHAR(15)    NOT NULL,
    Priority BIGINT NOT NULL
                     UNIQUE,
    PRIMARY KEY (ID)
);

CREATE TABLE Users (
    ID          BIGINT NOT NULL,
    Name        VARCHAR(50) NOT NULL,
    JoinDate    BIGINT NOT NULL,
    CreatedDate BIGINT NOT NULL,
    PrimaryRole BIGINT NOT NULL,
    LeftServer        VARCHAR(2) NOT NULL DEFAULT 'F',
    FOREIGN KEY (PrimaryRole) REFERENCES Roles (ID) ON UPDATE CASCADE,
    PRIMARY KEY (ID)
);

CREATE TABLE Credits (
    User    BIGINT NOT NULL,
    Credits BIGINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (User),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE
);

CREATE TABLE Dailies (
    User      BIGINT NOT NULL,
    DailyUses BIGINT NOT NULL
                      DEFAULT 0,
    LastDaily BIGINT NOT NULL
                      DEFAULT 0,
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    PRIMARY KEY (User)
);

CREATE TABLE FM (
    User BIGINT NOT NULL,
    LastFMUsername VARCHAR(100)  NOT NULL,
    LastUpdated BIGINT NOT NULL,
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    PRIMARY KEY (User)
);

CREATE TABLE Golds (
    User BIGINT NOT NULL, 
    TimeGiven BIGINT NOT NULL, 
    GivenBy BIGINT NOT NULL, 
    GoldID BIGINT NOT NULL AUTO_INCREMENT, 
    FOREIGN KEY(User) REFERENCES Users (ID) ON UPDATE CASCADE,
    FOREIGN KEY(GivenBy) REFERENCES Users (ID) ON UPDATE CASCADE,
    PRIMARY KEY (GoldID)
);

CREATE TABLE Levels (
    User BIGINT NOT NULL, 
    Level BIGINT NOT NULL DEFAULT 0, 
    Points BIGINT NOT NULL DEFAULT 0, 
    MonthLevel BIGINT NOT NULL DEFAULT 0, 
    MonthPoints BIGINT NOT NULL DEFAULT 0, 
    NextPoint BIGINT DEFAULT 0, 
    PRIMARY KEY (User), 
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE
);

CREATE TABLE Mutes (
    User BIGINT NOT NULL, 
    UnmuteTime BIGINT NOT NULL,
    PRIMARY KEY (User),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE
);

CREATE TABLE Reminders (
    User BIGINT NOT NULL,
    Reminder VARCHAR(200) NOT NULL, Date BIGINT NOT NULL, 
    RemindID BIGINT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (RemindID),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE
);

CREATE TABLE OwnedRoles (
    User         BIGINT NOT NULL,
    Role         BIGINT NOT NULL,
    PurchaseDate BIGINT NOT NULL,
    PurchaseID   BIGINT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (PurchaseID),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    FOREIGN KEY (Role) REFERENCES Roles (ID) ON UPDATE CASCADE
);

CREATE TABLE Tags (
    TagName VARCHAR(30) NOT NULL, 
    User BIGINT NOT NULL, 
    Content VARCHAR(3000) NOT NULL, 
    LastUpdated BIGINT NOT NULL, 
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE, 
    PRIMARY KEY (TagName)
);

CREATE TABLE TempBans (
    User      BIGINT NOT NULL,
    UnbanTime BIGINT NOT NULL,
    PRIMARY KEY (User),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE
);

CREATE TABLE Warnings (
    User     BIGINT NOT NULL,
    Reason   VARCHAR(200)    NOT NULL,
    Date     BIGINT NOT NULL,
    WarnedBy BIGINT NOT NULL,
    WarnID   BIGINT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (WarnID),
    FOREIGN KEY (User) REFERENCES Users (ID) ON UPDATE CASCADE,
    FOREIGN KEY (WarnedBy)REFERENCES Users (ID) ON UPDATE CASCADE
);
