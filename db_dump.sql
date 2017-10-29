CREATE DATABASE  IF NOT EXISTS `photoshare` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `photoshare`;

-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: localhost    Database: photoshare
-- ------------------------------------------------------
-- Server version	5.7.19-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(45) NOT NULL,
  `lastname` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `dateOfBirth` date NOT NULL,
  `homeTown` varchar(45) DEFAULT NULL,
  `gender` enum('M','F','O') NOT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
  (1,'asd','asd','test@bu.edu','2016-12-12','asd','M','asd'),
  (2,'asd','asd','test1@bu.edu','2016-12-12','asd','M','asd'),
  (3,'abc','abc','a@a.com','2016-10-02','abc','F','aaa'),
  (4,'pqr','pqr','p@p.com','2010-02-03','pqr','F','ppp'),
  (5,'lmn','lmn','l@l.com','2009-10-02','lmn','M','lll'),
  (6,'aaa','aaa','b@b.com','2012-01-01','aaa','M','bbb'),
  (7,'aaa','abc','abc@a.com','2012-01-01','pune','F','aaa');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `friends`
--

DROP TABLE IF EXISTS `friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `friends` (
  `userId` int(11) NOT NULL,
  `friendId` int(11) NOT NULL,
  PRIMARY KEY (`userId`,`friendId`),
  KEY `FK_1_idx` (`userId`),
  KEY `FK_2_idx` (`friendId`),
  CONSTRAINT `FK_1` FOREIGN KEY (`userId`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_2` FOREIGN KEY (`friendId`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `friends`
--

LOCK TABLES `friends` WRITE;
/*!40000 ALTER TABLE `friends` DISABLE KEYS */;
INSERT INTO `friends` VALUES
  (1,2),(1,3),(1,4),
  (2,1),(2,3),(2,5),
  (3,1),(3,2),(3,5),
  (4,1),
  (5,2),(5,3),
  (6,4),
  (7,5);
/*!40000 ALTER TABLE `friends` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `albums`
--

DROP TABLE IF EXISTS `albums`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `albums` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `owner` int(11) NOT NULL,
  `dateofcreation` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `FK_3_idx` (`owner`),
  CONSTRAINT `FK_3` FOREIGN KEY (`owner`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `albums`
--

LOCK TABLES `albums` WRITE;
/*!40000 ALTER TABLE `albums` DISABLE KEYS */;
INSERT INTO `albums` VALUES
  (1,'scenery',1,'2017-10-27 15:10:25'),
  (2,'animals',4,'2017-10-27 15:16:18'),
  (3,'scenery',3,'2017-10-27 15:23:26');
/*!40000 ALTER TABLE `albums` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos`
--

DROP TABLE IF EXISTS `photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `album` int(11) NOT NULL,
  `caption` varchar(45) DEFAULT NULL,
  `dir` varchar(45) DEFAULT NULL,
  `dateofcreation` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `FK_4_idx` (`album`),
  CONSTRAINT `FK_4` FOREIGN KEY (`album`) REFERENCES `albums` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos`
--

LOCK TABLES `photos` WRITE;
/*!40000 ALTER TABLE `photos` DISABLE KEYS */;
INSERT INTO `photos` VALUES
  (1,1,'sunset','/1/1.jpg','2017-10-27 15:13:09'),
  (2,1,'railway in a jungle','/1/2.jpg','2017-10-27 15:15:03'),
  (3,2,'tiger\'s leap','/4/1.jpg','2017-10-27 15:21:10'),
  (4,2,'tiger sitting','/4/2.jpg','2017-10-27 15:21:45'),
  (5,2,'blue bird sitting','/4/3.jpg','2017-10-27 15:22:37'),
  (6,3,'sunset from a dock','/3/1.jpeg','2017-10-27 15:23:56'),
  (7,3,'sunset from a blue beach','/3/2.jpeg','2017-10-27 15:24:22'),
  (8,3,'yoga on a mountain','/3/3.jpg','2017-10-27 15:27:25');
/*!40000 ALTER TABLE `photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `photoId` int(11) NOT NULL,
  `text` varchar(200) DEFAULT NULL,
  `user` int(11) NOT NULL,
  `dateofcreation` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `FK_5_idx` (`user`),
  KEY `FK_6_idx` (`photoId`),
  CONSTRAINT `FK_5` FOREIGN KEY (`user`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_6` FOREIGN KEY (`photoId`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES
  (1,3,'nice photo',1,'2017-10-29 14:42:33'),
  (2,6,'nice photo',3,'2017-10-29 14:43:51');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `likes`
--

DROP TABLE IF EXISTS `likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `likes` (
  `photo` int(11) NOT NULL,
  `user` int(11) NOT NULL,
  PRIMARY KEY (`photo`,`user`),
  KEY `FK_7_idx` (`user`),
  KEY `FK_8_idx` (`photo`),
  CONSTRAINT `FK_7` FOREIGN KEY (`user`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_8` FOREIGN KEY (`photo`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `likes`
--

LOCK TABLES `likes` WRITE;
/*!40000 ALTER TABLE `likes` DISABLE KEYS */;
INSERT INTO `likes` VALUES
  (2,1),
  (3,1),
  (6,3);
/*!40000 ALTER TABLE `likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES
  (1,'sunset'),
  (2,'rock'),
  (3,'ocean'),
  (4,'jungle'),
  (5,'railway'),
  (6,'scenic'),
  (7,'tiger'),
  (8,'leap'),
  (9,'sitting'),
  (10,'stare'),
  (11,'blue'),
  (12,'bird'),
  (13,'dock'),
  (14,'beach'),
  (15,'mountain'),
  (16,'yoga');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phototags`
--

DROP TABLE IF EXISTS `phototags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phototags` (
  `photoId` int(11) NOT NULL,
  `tagId` int(11) NOT NULL,
  PRIMARY KEY (`photoId`,`tagId`),
  KEY `FK_9_idx` (`photoId`),
  KEY `FK_10_idx` (`tagId`),
  CONSTRAINT `FK_9` FOREIGN KEY (`photoId`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_10` FOREIGN KEY (`tagId`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phototags`
--

LOCK TABLES `phototags` WRITE;
/*!40000 ALTER TABLE `phototags` DISABLE KEYS */;
INSERT INTO `phototags` VALUES
  (1,1),(1,2),(1,3),
  (2,4),(2,5),(2,6),
  (3,7),
  (4,7),(4,9),(4,10),
  (5,9),(5,11),(5,12),
  (6,1),(6,13),
  (7,1),(7,11),(7,14),
  (8,1),(8,15),(8,16);
/*!40000 ALTER TABLE `phototags` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-10-29 17:57:13
