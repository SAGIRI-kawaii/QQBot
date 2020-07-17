-- MySQL dump 10.13  Distrib 8.0.20, for Win64 (x86_64)
--
-- Host: localhost    Database: qqbot
-- ------------------------------------------------------
-- Server version	8.0.20

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `groupId` bigint DEFAULT NULL,
  `adminId` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blacklist`
--

DROP TABLE IF EXISTS `blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `blacklist` (
  `id` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `calledcount`
--

DROP TABLE IF EXISTS `calledcount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `calledcount` (
  `setuCalled` int DEFAULT NULL,
  `realCalled` int DEFAULT NULL,
  `bizhiCalled` int DEFAULT NULL,
  `weatherCalled` int DEFAULT NULL,
  `responseCalled` int DEFAULT NULL,
  `clockCalled` int DEFAULT NULL,
  `searchCount` int DEFAULT NULL,
  `botSetuCount` int NOT NULL,
  `dialsCount` int NOT NULL,
  `predictCount` int DEFAULT NULL,
  `yellowPredictCount` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `celebrityquotes`
--

DROP TABLE IF EXISTS `celebrityquotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `celebrityquotes` (
  `groupId` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `content` text,
  `format` char(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chatsession`
--

DROP TABLE IF EXISTS `chatsession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chatsession` (
  `groupId` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `session` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `city`
--

DROP TABLE IF EXISTS `city`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `city` (
  `id` varchar(32) NOT NULL,
  `cityEn` varchar(32) NOT NULL,
  `cityZh` varchar(32) NOT NULL,
  `provinceEn` varchar(32) NOT NULL,
  `provinceZh` varchar(32) NOT NULL,
  `countryEn` varchar(32) NOT NULL,
  `countryZh` varchar(32) NOT NULL,
  `leaderEn` varchar(32) NOT NULL,
  `leaderZh` varchar(32) NOT NULL,
  `lat` varchar(32) NOT NULL,
  `lon` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='城市表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clockchoice`
--

DROP TABLE IF EXISTS `clockchoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clockchoice` (
  `groupId` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `choice` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `functioncalled`
--

DROP TABLE IF EXISTS `functioncalled`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `functioncalled` (
  `time` datetime DEFAULT NULL,
  `operation` text,
  `sender` bigint DEFAULT NULL,
  `groupId` bigint DEFAULT NULL,
  `result` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `imgcalled`
--

DROP TABLE IF EXISTS `imgcalled`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imgcalled` (
  `time` datetime DEFAULT NULL,
  `operation` text,
  `picUrl` text,
  `sender` bigint DEFAULT NULL,
  `groupId` bigint DEFAULT NULL,
  `result` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jokes`
--

DROP TABLE IF EXISTS `jokes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jokes` (
  `text` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `memberpiccount`
--

DROP TABLE IF EXISTS `memberpiccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `memberpiccount` (
  `groupId` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `count` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `predictready`
--

DROP TABLE IF EXISTS `predictready`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `predictready` (
  `groupId` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `status` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `searchready`
--

DROP TABLE IF EXISTS `searchready`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `searchready` (
  `groupId` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `status` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `setting`
--

DROP TABLE IF EXISTS `setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `setting` (
  `groupId` bigint DEFAULT NULL,
  `groupName` varchar(20) NOT NULL,
  `repeat` tinyint(1) DEFAULT NULL,
  `setuLocal` tinyint(1) DEFAULT NULL,
  `bizhiLocal` tinyint(1) DEFAULT NULL,
  `countLimit` tinyint(1) DEFAULT NULL,
  `limit` int DEFAULT NULL,
  `setu` tinyint(1) DEFAULT NULL,
  `bizhi` tinyint(1) DEFAULT NULL,
  `real` tinyint(1) DEFAULT NULL,
  `r18` tinyint(1) DEFAULT NULL,
  `search` tinyint(1) DEFAULT NULL,
  `imgPredict` tinyint(1) DEFAULT NULL,
  `yellowPredict` tinyint(1) DEFAULT NULL,
  `imgLightning` tinyint(1) DEFAULT NULL,
  `speakMode` char(10) DEFAULT NULL,
  `switch` char(10) DEFAULT NULL,
  `forbiddenCount` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `yellowpredictready`
--

DROP TABLE IF EXISTS `yellowpredictready`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `yellowpredictready` (
  `groupid` bigint DEFAULT NULL,
  `memberId` bigint DEFAULT NULL,
  `status` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-07-18  3:18:06
