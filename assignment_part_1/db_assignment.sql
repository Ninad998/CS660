CREATE DATABASE IF NOT EXISTS `db_assignment` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `db_assignment`;

DROP TABLE IF EXISTS `likes`;
DROP TABLE IF EXISTS `phototags`;
DROP TABLE IF EXISTS `tags`;
DROP TABLE IF EXISTS `comments`;
DROP TABLE IF EXISTS `photos`;
DROP TABLE IF EXISTS `albums`;
DROP TABLE IF EXISTS `friends`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(45) NOT NULL,
  `lastname` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `dateOfBirth` date DEFAULT NULL,
  `homeTown` varchar(45) DEFAULT NULL,
  `gender` enum('M','F') DEFAULT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `friends` (
  `userId` int(11) NOT NULL,
  `friendId` int(11) NOT NULL,
  PRIMARY KEY (`userId`,`friendId`),
  KEY `FK_1_idx` (`friendId`),
  KEY `FK_2_idx` (`friendId`),
  CONSTRAINT `FK_1` FOREIGN KEY (`userId`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_2` FOREIGN KEY (`friendId`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `albums` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `owner` int(11) NOT NULL,
  `dateofcreation` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_3_idx` (`owner`),
  CONSTRAINT `FK_3` FOREIGN KEY (`owner`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `photos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `album` int(11) NOT NULL,
  `caption` varchar(45) DEFAULT NULL,
  `data` blob,
  PRIMARY KEY (`id`),
  KEY `FK_4_idx` (`album`),
  CONSTRAINT `FK_4` FOREIGN KEY (`album`) REFERENCES `albums` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `photo_id` int(11) NOT NULL,
  `text` varchar(200) DEFAULT NULL,
  `user` int(11) NOT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_5_idx` (`user`),
  KEY `FK_6_idx` (`photo_id`),
  CONSTRAINT `FK_5` FOREIGN KEY (`user`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_6` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `tags` (
  `id` int(11) NOT NULL,
  `word` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `phototags` (
  `photoId` int(11) NOT NULL,
  `tagId` int(11) NOT NULL,
  PRIMARY KEY (`photoId`,`tagId`),
  KEY `FK_7_idx` (`photoId`),
  KEY `FK_8_idx` (`tagId`),
  CONSTRAINT `FK_7` FOREIGN KEY (`photoId`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_8` FOREIGN KEY (`tagId`) REFERENCES `tags` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `likes` (
  `photo` int(11) NOT NULL,
  `user` int(11) NOT NULL,
  PRIMARY KEY (`photo`,`user`),
  KEY `FK_9_idx` (`photo`),
  KEY `FK_10_idx` (`user`),
  CONSTRAINT `FK_9` FOREIGN KEY (`photo`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_10` FOREIGN KEY (`user`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
