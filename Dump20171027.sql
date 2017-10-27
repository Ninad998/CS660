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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'asd','asd','test@bu.edu','2016-12-12','asd','M','asd'),(7,'asd','asd','test1@bu.edu','2016-12-12','asd','M','asd'),(8,'abc','abc','a@a.com','2016-10-02','abc','F','aaa'),(9,'pqr','pqr','p@p.com','2010-02-03','pqr','F','ppp'),(10,'lmn','lmn','l@l.com','2009-10-02','lmn','M','lll'),(11,'aaa','aaa','b@b.com','2012-01-01','aaa','M','bbb'),(12,'aaa','abc','abc@a.com','1966-06-20','pune','F','aaa');
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
INSERT INTO `friends` VALUES (7,1),(1,7),(12,7),(1,8),(7,8),(11,8),(7,9),(8,9),(10,9),(11,9),(8,10),(9,10),(1,11),(7,12);
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
INSERT INTO `albums` VALUES (1,'check',1,'2017-10-14 17:38:35'),(3,'alb',12,'2017-10-27 11:19:14');
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
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos`
--

LOCK TABLES `photos` WRITE;
/*!40000 ALTER TABLE `photos` DISABLE KEYS */;
INSERT INTO `photos` VALUES (5,1,'asd','/1/4.jpeg','2017-10-17 18:24:29'),(6,1,'asd','/1/5.jpeg','2017-10-17 18:24:29'),(7,1,'asd','/1/1.jpeg','2017-10-17 17:26:59'),(10,1,'asd','/1/2.jpeg','2017-10-17 17:26:59'),(11,1,'asd','/1/3.jpeg','2017-10-17 17:26:59'),(12,1,'asd','/1/6.jpeg','2017-10-17 18:13:11'),(13,1,'asd','/1/7.jpeg','2017-10-17 18:14:57'),(14,1,'asd','/1/8.jpeg','2017-10-17 18:23:08'),(16,3,'cap','/12/4.jpeg','2017-10-27 11:19:33'),(17,3,'cap2','/12/5.jpeg','2017-10-27 11:23:07'),(18,1,'asd','/1/9.jpeg','2017-10-27 11:59:29'),(19,1,'asdf','/1/10.jpeg','2017-10-27 11:59:51');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (2,5,'Check 1',1,'2017-10-23 19:40:46'),(3,5,'Check 2',1,'2017-10-23 19:42:33'),(5,5,'Check 3',1,'2017-10-27 12:33:40'),(6,11,'Check 1',1,'2017-10-27 12:34:11');
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
INSERT INTO `likes` VALUES (5,1),(7,1),(11,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'asd'),(2,'asd1'),(3,'asd2'),(4,'asd3'),(5,'tags1'),(6,'ttt'),(7,'www'),(8,'asdf');
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
  KEY `FK_9_idx` (`tagId`),
  KEY `FK_10_idx` (`photoId`),
  CONSTRAINT `FK_9` FOREIGN KEY (`tagId`) REFERENCES `tags` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_10` FOREIGN KEY (`photoId`) REFERENCES `photos` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phototags`
--

LOCK TABLES `phototags` WRITE;
/*!40000 ALTER TABLE `phototags` DISABLE KEYS */;
INSERT INTO `phototags` VALUES (7,1),(7,2),(7,3),(7,4),(10,3),(10,4),(11,1),(11,2),(11,4),(12,4),(13,1),(13,2),(16,5),(17,1),(17,5),(17,6),(17,7),(18,1),(19,8);
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

-- Dump completed on 2017-10-27 12:36:09
