use PIN;
drop table if exists entries;

CREATE TABLE entries (
  id INT(50) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  title TEXT NOT NULL,
  text TEXT NOT NULL
);