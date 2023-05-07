Create DataBase TT_Bot;

Use TT_Bot;

CREATE TABLE TestTable (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    IdTgUser BIGINT NOT NULL -- В идеале должно ещё быть UNIQUE, но пока оставил так
);
